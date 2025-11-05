/**
 * Shared types for category tree components
 */

/**
 * Category tree node interface for hierarchical category structure
 */
export interface CategoryTreeNode {
  name: string
  fullName: string
  count: number
  children: CategoryTreeNode[]
}
