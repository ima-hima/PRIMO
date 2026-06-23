import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const mountEl = document.getElementById('react-tree-root');
if (mountEl) {
  const treeData = window.PRIMO_TREE_DATA || [];
  const initialSelection = window.PRIMO_INITIAL_SELECTION || {};

  const root = ReactDOM.createRoot(mountEl);
  root.render(
    <React.StrictMode>
      <App treeData={treeData} initialSelection={initialSelection} />
    </React.StrictMode>
  );
}
