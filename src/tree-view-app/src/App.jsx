import { useState } from "react";
import TreeNode from "./TreeView";
import "./TreeView/styles.css";

function getAllLeaves(nodes) {
  return nodes.flatMap(node =>
    !node.children?.length ? [node] : getAllLeaves(node.children)
  );
}

function App({ treeData, initialSelection }) {
  const [selected, setSelected] = useState(initialSelection || {});

  const handleSelect = (id, checked) => {
    setSelected(prev => ({ ...prev, [id]: checked }));
  };

  const leaves = getAllLeaves(treeData);
  const selectedLeafIds = leaves.filter(l => selected[l.id]).map(l => l.id);

  return (
    <div className="tree-view-container">
      {selectedLeafIds.map(id => (
        <input key={id} type="hidden" name="id" value={id} />
      ))}
      {treeData.map(node => (
        <TreeNode
          key={node.id}
          taxon={node}
          selected={selected}
          onSelect={handleSelect}
        />
      ))}
    </div>
  );
}

export default App;
