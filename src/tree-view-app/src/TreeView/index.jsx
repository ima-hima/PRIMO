import { useEffect, useRef, useState } from "react";
import { FaChevronDown, FaChevronRight } from 'react-icons/fa';
import { getAllLeafDescendantIds } from "./treeUtils";
import "./styles.css";

function hasSelectedDescendant(node, selected) {
  return (node.children || []).some(
    child => selected[child.id] || hasSelectedDescendant(child, selected)
  );
}

function TreeNode({ taxon, selected, onSelect, expandAll = false }) {
  const hasChildren = taxon.children?.length > 0;
  const [expanded, setExpanded] = useState(
    taxon.expand_in_tree || (hasChildren && hasSelectedDescendant(taxon, selected))
  );
  const [expandAllChildren, setExpandAllChildren] = useState(false);
  const checkboxRef = useRef(null);

  useEffect(() => {
    if (expandAll) {
      setExpanded(true);
      setExpandAllChildren(true);
    }
  }, [expandAll]);

  // For non-leaf nodes, derive checked/indeterminate from leaf descendants only.
  // This prevents stale selected[non_leaf_id] values from corrupting ancestor state.
  const leafDescendantIds = hasChildren ? getAllLeafDescendantIds(taxon) : [];
  const checkedLeafCount = leafDescendantIds.filter(id => selected[id]).length;
  const isChecked = hasChildren
    ? checkedLeafCount === leafDescendantIds.length && leafDescendantIds.length > 0
    : !!selected[taxon.id];
  const isIndeterminate = hasChildren && checkedLeafCount > 0 && !isChecked;

  useEffect(() => {
    if (checkboxRef.current) {
      checkboxRef.current.indeterminate = isIndeterminate;
    }
  }, [isIndeterminate]);

  const handleChange = (checked) => {
    if (hasChildren) {
      leafDescendantIds.forEach(id => onSelect(id, checked));
    } else {
      onSelect(taxon.id, checked);
    }
  };

  const handleToggle = (e) => {
    if (e.altKey) {
      setExpanded(true);
      setExpandAllChildren(true);
    } else {
      setExpanded(prev => !prev);
      setExpandAllChildren(false);
    }
  };

  return (
    <div className="tree-node">
      <div className={`tree-node-row${hasChildren ? " has-children" : ""}`}>
        {hasChildren ? (
          <span className="clickable" onClick={handleToggle}>
            {expanded
              ? <FaChevronDown color="#006699" size={11} />
              : <FaChevronRight color="#006699" size={11} />}
          </span>
        ) : (
          <span className="tree-node-spacer" />
        )}
        <label>
          <input
            ref={checkboxRef}
            type="checkbox"
            checked={isChecked}
            onChange={(e) => handleChange(e.target.checked)}
          />
          {" "}{taxon.label}
        </label>
      </div>

      {expanded && hasChildren && (
        <div style={{ paddingLeft: 20 }}>
          {taxon.children.map(child => (
            <TreeNode
              key={child.id}
              taxon={child}
              selected={selected}
              onSelect={onSelect}
              expandAll={expandAllChildren}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default TreeNode;
