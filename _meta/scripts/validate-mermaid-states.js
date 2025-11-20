#!/usr/bin/env node

/**
 * Mermaid State Diagram Validator
 * 
 * This script validates mermaid state diagrams in the repository.
 * It checks for:
 * - Syntax validity
 * - State name consistency
 * - Transition completeness
 * - Terminal state reachability
 */

const fs = require('fs');
const path = require('path');

class MermaidStateValidator {
    constructor() {
        this.states = new Set();
        this.transitions = [];
        this.compositeStates = new Map();
        this.errors = [];
        this.warnings = [];
        this.startState = null;
        this.terminalStates = new Set();
    }

    /**
     * Extract mermaid diagrams from a markdown file
     */
    extractMermaidDiagrams(filePath) {
        const content = fs.readFileSync(filePath, 'utf-8');
        const diagrams = [];
        const lines = content.split('\n');
        let inMermaid = false;
        let currentDiagram = [];
        let startLine = -1;

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (line.trim() === '```mermaid') {
                inMermaid = true;
                startLine = i + 1;
                currentDiagram = [];
            } else if (inMermaid && line.trim() === '```') {
                inMermaid = false;
                diagrams.push({
                    content: currentDiagram.join('\n'),
                    startLine: startLine,
                    endLine: i
                });
            } else if (inMermaid) {
                currentDiagram.push(line);
            }
        }

        return diagrams;
    }

    /**
     * Parse a state diagram
     */
    parseStateDiagram(diagramContent) {
        const lines = diagramContent.split('\n');
        let currentCompositeState = null;

        for (const line of lines) {
            const trimmed = line.trim();
            
            // Skip empty lines and comments
            if (!trimmed || trimmed.startsWith('%%')) continue;
            
            // Check if it's a state diagram
            if (trimmed.startsWith('stateDiagram')) continue;

            // Handle composite state start
            if (trimmed.match(/^state\s+(\w+)\s*\{/)) {
                const match = trimmed.match(/^state\s+(\w+)\s*\{/);
                currentCompositeState = match[1];
                this.states.add(currentCompositeState);
                this.compositeStates.set(currentCompositeState, []);
                continue;
            }

            // Handle composite state end
            if (trimmed === '}') {
                currentCompositeState = null;
                continue;
            }

            // Handle transitions
            if (trimmed.includes('-->')) {
                const parts = trimmed.split('-->').map(p => p.trim());
                if (parts.length === 2) {
                    let fromState = parts[0];
                    let toState = parts[1].split(/\s+/)[0]; // Remove any comments

                    // Handle [*] as start/end states
                    if (fromState === '[*]') {
                        fromState = '__START__';
                        if (!this.startState && !currentCompositeState) {
                            this.startState = toState;
                        }
                    }
                    if (toState === '[*]') {
                        toState = '__END__';
                    }

                    // Add states
                    if (fromState !== '__START__' && fromState !== '__END__') {
                        this.states.add(fromState);
                    }
                    if (toState !== '__START__' && toState !== '__END__') {
                        this.states.add(toState);
                    }

                    // Track transitions
                    this.transitions.push({ from: fromState, to: toState });

                    // Track composite state substates
                    if (currentCompositeState) {
                        const substates = this.compositeStates.get(currentCompositeState);
                        if (!substates.includes(fromState) && fromState !== '__START__') {
                            substates.push(fromState);
                        }
                        if (!substates.includes(toState) && toState !== '__END__') {
                            substates.push(toState);
                        }
                    }
                }
            }
        }
    }

    /**
     * Validate the parsed diagram
     */
    validate() {
        // Check for start state
        if (!this.startState) {
            this.errors.push('No start state found. State diagram should have [*] --> InitialState');
        }

        // Find terminal states (states that only transition to themselves or have no outgoing transitions except to terminal)
        const statesWithOutgoing = new Set();
        const statesTransitioningToEnd = new Set();
        
        for (const transition of this.transitions) {
            if (transition.from !== '__START__' && transition.from !== '__END__') {
                statesWithOutgoing.add(transition.from);
            }
            if (transition.to === '__END__') {
                statesTransitioningToEnd.add(transition.from);
            }
        }

        // Find states that could be terminal states
        for (const state of this.states) {
            const outgoingTransitions = this.transitions.filter(t => t.from === state);
            const hasOnlyArchiveTransition = outgoingTransitions.every(t => 
                t.to === 'Archived' || t.to === state
            );
            
            if (state === 'Archived' || hasOnlyArchiveTransition) {
                this.terminalStates.add(state);
            }
        }

        // Check for unreachable states
        const reachableStates = new Set();
        if (this.startState) {
            this.findReachableStates(this.startState, reachableStates);
        }

        // Get all substates of composite states
        const allSubstates = new Set();
        for (const [compositeName, substates] of this.compositeStates) {
            substates.forEach(s => allSubstates.add(s));
        }

        for (const state of this.states) {
            // Skip substates of composite states as they have their own entry/exit points
            if (allSubstates.has(state)) continue;
            
            if (!reachableStates.has(state) && state !== this.startState) {
                this.warnings.push(`State '${state}' may not be reachable from the start state`);
            }
        }

        // Check that terminal states can be reached
        const canReachTerminal = Array.from(this.terminalStates).some(ts => reachableStates.has(ts));
        if (this.terminalStates.size > 0 && !canReachTerminal) {
            this.warnings.push('No path found to any terminal state');
        }

        // Check for states with no outgoing transitions (except terminal states)
        for (const state of this.states) {
            const outgoing = this.transitions.filter(t => t.from === state);
            if (outgoing.length === 0 && !this.terminalStates.has(state)) {
                this.warnings.push(`State '${state}' has no outgoing transitions (not marked as terminal)`);
            }
        }

        // Validate composite states
        for (const [compositeName, substates] of this.compositeStates) {
            // Check if composite state has entry/exit points
            const hasEntry = this.transitions.some(t => 
                t.from === '__START__' && substates.includes(t.to)
            );
            const hasExit = this.transitions.some(t => 
                substates.includes(t.from) && t.to === '__END__'
            );

            if (!hasEntry) {
                this.warnings.push(`Composite state '${compositeName}' has no entry point [*] --> substate`);
            }
            if (!hasExit) {
                this.warnings.push(`Composite state '${compositeName}' has no exit point substate --> [*]`);
            }
        }
    }

    /**
     * Find all reachable states from a given state
     */
    findReachableStates(state, reachable) {
        if (reachable.has(state)) return;
        reachable.add(state);

        const nextStates = this.transitions
            .filter(t => t.from === state)
            .map(t => t.to)
            .filter(s => s !== '__END__');

        for (const nextState of nextStates) {
            this.findReachableStates(nextState, reachable);
        }
    }

    /**
     * Generate a validation report
     */
    generateReport(filePath, diagram) {
        const report = {
            file: filePath,
            diagramLocation: `Lines ${diagram.startLine}-${diagram.endLine}`,
            states: Array.from(this.states).sort(),
            stateCount: this.states.size,
            transitionCount: this.transitions.length,
            compositeStates: Array.from(this.compositeStates.keys()),
            startState: this.startState,
            terminalStates: Array.from(this.terminalStates).sort(),
            errors: this.errors,
            warnings: this.warnings,
            isValid: this.errors.length === 0
        };

        return report;
    }
}

/**
 * Main function
 */
function main() {
    const workflowFile = path.join(__dirname, '../../WORKFLOW.md');
    
    console.log('🔍 Validating Mermaid State Diagrams\n');
    console.log(`File: ${workflowFile}\n`);

    if (!fs.existsSync(workflowFile)) {
        console.error(`❌ Error: File not found: ${workflowFile}`);
        process.exit(1);
    }

    const validator = new MermaidStateValidator();
    const diagrams = validator.extractMermaidDiagrams(workflowFile);

    if (diagrams.length === 0) {
        console.log('⚠️  No mermaid diagrams found in the file');
        process.exit(0);
    }

    console.log(`Found ${diagrams.length} mermaid diagram(s)\n`);

    let hasErrors = false;

    diagrams.forEach((diagram, index) => {
        console.log(`\n${'='.repeat(70)}`);
        console.log(`📊 Diagram #${index + 1} (Lines ${diagram.startLine}-${diagram.endLine})`);
        console.log('='.repeat(70));

        const diagramValidator = new MermaidStateValidator();
        
        // Check if it's a state diagram
        if (!diagram.content.includes('stateDiagram')) {
            console.log('ℹ️  Skipping - Not a state diagram\n');
            return;
        }

        diagramValidator.parseStateDiagram(diagram.content);
        diagramValidator.validate();
        const report = diagramValidator.generateReport(workflowFile, diagram);

        // Print summary
        console.log('\n📈 Summary:');
        console.log(`  States: ${report.stateCount}`);
        console.log(`  Transitions: ${report.transitionCount}`);
        console.log(`  Composite States: ${report.compositeStates.length}`);
        console.log(`  Start State: ${report.startState || 'Not found'}`);
        console.log(`  Terminal States: ${report.terminalStates.join(', ') || 'None'}`);

        // Print states
        console.log('\n📋 States Found:');
        report.states.forEach(state => {
            const isComposite = report.compositeStates.includes(state);
            const isTerminal = report.terminalStates.includes(state);
            const markers = [];
            if (isComposite) markers.push('composite');
            if (isTerminal) markers.push('terminal');
            const marker = markers.length > 0 ? ` [${markers.join(', ')}]` : '';
            console.log(`  - ${state}${marker}`);
        });

        if (report.compositeStates.length > 0) {
            console.log('\n🔲 Composite States:');
            report.compositeStates.forEach(cs => {
                const substates = diagramValidator.compositeStates.get(cs);
                console.log(`  - ${cs}:`);
                substates.forEach(ss => console.log(`      → ${ss}`));
            });
        }

        // Print errors
        if (report.errors.length > 0) {
            console.log('\n❌ Errors:');
            report.errors.forEach(err => console.log(`  - ${err}`));
            hasErrors = true;
        } else {
            console.log('\n✅ No errors found');
        }

        // Print warnings
        if (report.warnings.length > 0) {
            console.log('\n⚠️  Warnings:');
            report.warnings.forEach(warn => console.log(`  - ${warn}`));
        }

        // Final verdict
        console.log('\n' + '─'.repeat(70));
        if (report.isValid) {
            console.log('✅ Diagram is VALID');
        } else {
            console.log('❌ Diagram has ERRORS');
        }
        console.log('─'.repeat(70));
    });

    console.log('\n\n' + '='.repeat(70));
    if (hasErrors) {
        console.log('❌ VALIDATION FAILED - Errors found');
        console.log('='.repeat(70));
        process.exit(1);
    } else {
        console.log('✅ VALIDATION PASSED - All diagrams are valid');
        console.log('='.repeat(70));
        process.exit(0);
    }
}

// Run the validator
if (require.main === module) {
    main();
}

module.exports = MermaidStateValidator;
