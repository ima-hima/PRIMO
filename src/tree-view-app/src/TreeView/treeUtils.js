export function getAllDescendantIds(node) {
  if (!node.children) return [];
  return node.children.flatMap(child => [
    child.id,
    ...getAllDescendantIds(child)
  ]);
}

// Returns IDs of leaf descendants only (nodes with no children).
// Does not include node itself.
export function getAllLeafDescendantIds(node) {
  if (!node.children || node.children.length === 0) return [];
  return node.children.flatMap(child =>
    child.children?.length > 0 ? getAllLeafDescendantIds(child) : [child.id]
  );
}
