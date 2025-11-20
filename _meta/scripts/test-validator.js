#!/usr/bin/env node

/**
 * Test suite for Mermaid State Diagram Validator
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const MermaidStateValidator = require('./validate-mermaid-states.js');

// Test cases
const testCases = [
    {
        name: 'Valid Simple State Diagram',
        content: `
\`\`\`mermaid
stateDiagram-v2
    [*] --> StateA
    StateA --> StateB
    StateB --> [*]
\`\`\`
`,
        expectedValid: true,
        expectedStates: ['StateA', 'StateB'],
        expectedStartState: 'StateA'
    },
    {
        name: 'Valid State Diagram with Composite State',
        content: `
\`\`\`mermaid
stateDiagram-v2
    [*] --> StateA
    
    state StateA {
        [*] --> SubA1
        SubA1 --> SubA2
        SubA2 --> [*]
    }
    
    StateA --> StateB
    StateB --> [*]
\`\`\`
`,
        expectedValid: true,
        expectedStates: ['StateA', 'StateB', 'SubA1', 'SubA2'],
        expectedCompositeStates: ['StateA']
    },
    {
        name: 'State Diagram with Multiple Transitions',
        content: `
\`\`\`mermaid
stateDiagram-v2
    [*] --> Start
    Start --> Processing
    Processing --> Success
    Processing --> Error
    Success --> [*]
    Error --> [*]
\`\`\`
`,
        expectedValid: true,
        expectedStates: ['Start', 'Processing', 'Success', 'Error']
    },
    {
        name: 'State Diagram with Comments',
        content: `
\`\`\`mermaid
stateDiagram-v2
    [*] --> Start
    Start --> End  %% This is a comment
    End --> [*]
\`\`\`
`,
        expectedValid: true,
        expectedStates: ['Start', 'End']
    },
    {
        name: 'Empty Diagram (No Start State)',
        content: `
\`\`\`mermaid
stateDiagram-v2
    StateA --> StateB
\`\`\`
`,
        expectedValid: false,
        expectedErrors: 1  // Missing start state
    }
];

function runTests() {
    console.log('🧪 Running Mermaid State Validator Tests\n');
    console.log('='.repeat(70));
    
    let passed = 0;
    let failed = 0;
    
    testCases.forEach((testCase, index) => {
        console.log(`\nTest ${index + 1}: ${testCase.name}`);
        console.log('-'.repeat(70));
        
        const validator = new MermaidStateValidator();
        
        // Extract and parse diagram
        const tempFile = path.join(os.tmpdir(), `test-mermaid-${index}.md`);
        fs.writeFileSync(tempFile, testCase.content);
        
        const diagrams = validator.extractMermaidDiagrams(tempFile);
        
        if (diagrams.length === 0) {
            console.log('❌ FAILED: No diagram found');
            failed++;
            fs.unlinkSync(tempFile);
            return;
        }
        
        validator.parseStateDiagram(diagrams[0].content);
        validator.validate();
        
        const isValid = validator.errors.length === 0;
        let testPassed = true;
        
        // Check validity
        if (isValid !== testCase.expectedValid) {
            console.log(`❌ FAILED: Expected valid=${testCase.expectedValid}, got valid=${isValid}`);
            testPassed = false;
        }
        
        // Check expected states
        if (testCase.expectedStates) {
            const actualStates = Array.from(validator.states).sort();
            const expectedStates = testCase.expectedStates.sort();
            
            const missingStates = expectedStates.filter(s => !actualStates.includes(s));
            const extraStates = actualStates.filter(s => !expectedStates.includes(s));
            
            if (missingStates.length > 0 || extraStates.length > 0) {
                console.log(`❌ FAILED: State mismatch`);
                if (missingStates.length > 0) {
                    console.log(`   Missing: ${missingStates.join(', ')}`);
                }
                if (extraStates.length > 0) {
                    console.log(`   Extra: ${extraStates.join(', ')}`);
                }
                testPassed = false;
            }
        }
        
        // Check start state
        if (testCase.expectedStartState) {
            if (validator.startState !== testCase.expectedStartState) {
                console.log(`❌ FAILED: Expected start state '${testCase.expectedStartState}', got '${validator.startState}'`);
                testPassed = false;
            }
        }
        
        // Check composite states
        if (testCase.expectedCompositeStates) {
            const actualComposite = Array.from(validator.compositeStates.keys()).sort();
            const expectedComposite = testCase.expectedCompositeStates.sort();
            
            if (JSON.stringify(actualComposite) !== JSON.stringify(expectedComposite)) {
                console.log(`❌ FAILED: Composite state mismatch`);
                console.log(`   Expected: ${expectedComposite.join(', ')}`);
                console.log(`   Got: ${actualComposite.join(', ')}`);
                testPassed = false;
            }
        }
        
        // Check error count
        if (testCase.expectedErrors !== undefined) {
            if (validator.errors.length !== testCase.expectedErrors) {
                console.log(`❌ FAILED: Expected ${testCase.expectedErrors} errors, got ${validator.errors.length}`);
                testPassed = false;
            }
        }
        
        if (testPassed) {
            console.log('✅ PASSED');
            passed++;
        } else {
            console.log('\nValidator Output:');
            console.log(`  States: ${Array.from(validator.states).join(', ')}`);
            console.log(`  Start State: ${validator.startState}`);
            console.log(`  Errors: ${validator.errors.length}`);
            if (validator.errors.length > 0) {
                validator.errors.forEach(e => console.log(`    - ${e}`));
            }
            failed++;
        }
        
        // Cleanup
        fs.unlinkSync(tempFile);
    });
    
    console.log('\n' + '='.repeat(70));
    console.log(`\n📊 Test Results: ${passed}/${testCases.length} passed, ${failed} failed\n`);
    
    if (failed === 0) {
        console.log('✅ All tests passed!');
        process.exit(0);
    } else {
        console.log('❌ Some tests failed');
        process.exit(1);
    }
}

// Run tests
runTests();
