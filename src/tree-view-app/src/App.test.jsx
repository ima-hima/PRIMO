import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';
import TreeNode from './TreeView';

// Minimal tree fixture: one root with two children
const singleNode = [{ id: 1, label: 'Root', expand_in_tree: false, children: [] }];

const parentWithChildren = [
  {
    id: 1, label: 'Parent', expand_in_tree: true,
    children: [
      { id: 2, label: 'Child A', expand_in_tree: false, children: [] },
      { id: 3, label: 'Child B', expand_in_tree: false, children: [] },
    ],
  },
];

const deepTree = [
  {
    id: 1, label: 'Root', expand_in_tree: true,
    children: [
      {
        id: 2, label: 'Middle', expand_in_tree: true,
        children: [
          { id: 3, label: 'Leaf', expand_in_tree: false, children: [] },
        ],
      },
    ],
  },
];

// ── App ──────────────────────────────────────────────────────────────────────

test('renders root node label', () => {
  render(<App treeData={singleNode} initialSelection={{}} />);
  expect(screen.getByText('Root')).toBeInTheDocument();
});

test('renders nothing when treeData is empty', () => {
  const { container } = render(<App treeData={[]} initialSelection={{}} />);
  expect(container.querySelector('input[type="checkbox"]')).toBeNull();
});

test('pre-checks nodes listed in initialSelection', () => {
  render(<App treeData={singleNode} initialSelection={{ '1': true }} />);
  expect(screen.getByRole('checkbox')).toBeChecked();
});

// ── Expand / collapse ─────────────────────────────────────────────────────────

test('children hidden when expand_in_tree is false', () => {
  const tree = [
    {
      id: 1, label: 'Parent', expand_in_tree: false,
      children: [{ id: 2, label: 'Child', expand_in_tree: false, children: [] }],
    },
  ];
  render(<App treeData={tree} initialSelection={{}} />);
  expect(screen.queryByText('Child')).toBeNull();
});

test('children visible when expand_in_tree is true', () => {
  render(<App treeData={parentWithChildren} initialSelection={{}} />);
  expect(screen.getByText('Child A')).toBeInTheDocument();
  expect(screen.getByText('Child B')).toBeInTheDocument();
});

test('clicking expand icon shows children', () => {
  const tree = [
    {
      id: 1, label: 'Parent', expand_in_tree: false,
      children: [{ id: 2, label: 'Hidden Child', expand_in_tree: false, children: [] }],
    },
  ];
  const { container } = render(<App treeData={tree} initialSelection={{}} />);
  expect(screen.queryByText('Hidden Child')).toBeNull();
  fireEvent.click(container.querySelector('.clickable'));
  expect(screen.getByText('Hidden Child')).toBeInTheDocument();
});

// ── Checkbox behaviour ────────────────────────────────────────────────────────

test('checking parent checks all children', () => {
  render(<App treeData={parentWithChildren} initialSelection={{}} />);
  const checkboxes = screen.getAllByRole('checkbox');
  // checkboxes[0] is the parent
  fireEvent.click(checkboxes[0]);
  screen.getAllByRole('checkbox').forEach(cb => {
    expect(cb).toBeChecked();
  });
});

test('unchecking parent unchecks all children', () => {
  const allSelected = { '1': true, '2': true, '3': true };
  render(<App treeData={parentWithChildren} initialSelection={allSelected} />);
  const checkboxes = screen.getAllByRole('checkbox');
  fireEvent.click(checkboxes[0]);
  screen.getAllByRole('checkbox').forEach(cb => {
    expect(cb).not.toBeChecked();
  });
});

test('checking a child does not check siblings', () => {
  render(<App treeData={parentWithChildren} initialSelection={{}} />);
  const checkboxes = screen.getAllByRole('checkbox');
  // checkboxes[1] is Child A, checkboxes[2] is Child B
  fireEvent.click(checkboxes[1]);
  expect(checkboxes[1]).toBeChecked();
  expect(checkboxes[2]).not.toBeChecked();
});

test('visible checkboxes have no name attribute (form submission uses hidden inputs)', () => {
  render(<App treeData={singleNode} initialSelection={{}} />);
  expect(screen.getByRole('checkbox')).not.toHaveAttribute('name');
});

test('selecting a leaf renders a hidden input with name="id" and the leaf value', () => {
  const { container } = render(<App treeData={singleNode} initialSelection={{}} />);
  fireEvent.click(screen.getByRole('checkbox'));
  const hidden = container.querySelector('input[type="hidden"][name="id"]');
  expect(hidden).not.toBeNull();
  expect(hidden.value).toBe('1');
});

test('selecting a collapsed non-leaf submits hidden inputs for its leaf descendants', () => {
  const collapsed = [{
    id: 1, label: 'Parent', expand_in_tree: false,
    children: [
      { id: 2, label: 'Child A', expand_in_tree: false, children: [] },
      { id: 3, label: 'Child B', expand_in_tree: false, children: [] },
    ],
  }];
  const { container } = render(<App treeData={collapsed} initialSelection={{}} />);
  // Only parent checkbox is visible (collapsed); click it
  fireEvent.click(screen.getByRole('checkbox'));
  const hiddenIds = [...container.querySelectorAll('input[type="hidden"][name="id"]')]
    .map(el => el.value);
  expect(hiddenIds).toContain('2');
  expect(hiddenIds).toContain('3');
  expect(hiddenIds).not.toContain('1');
});

test('deselecting a leaf removes its hidden input', () => {
  const { container } = render(<App treeData={singleNode} initialSelection={{ '1': true }} />);
  expect(container.querySelector('input[type="hidden"][name="id"]')).not.toBeNull();
  fireEvent.click(screen.getByRole('checkbox'));
  expect(container.querySelector('input[type="hidden"][name="id"]')).toBeNull();
});

// ── Deep tree ─────────────────────────────────────────────────────────────────

test('node with a selected descendant starts expanded even if expand_in_tree is false', () => {
  const tree = [{
    id: 1, label: 'Parent', expand_in_tree: false,
    children: [{ id: 2, label: 'Child', expand_in_tree: false, children: [] }],
  }];
  render(<App treeData={tree} initialSelection={{ '2': true }} />);
  expect(screen.getByText('Child')).toBeInTheDocument();
});

test('alt-click on expand icon expands all nested subtrees', () => {
  const collapsedDeep = [{
    id: 1, label: 'Root', expand_in_tree: false,
    children: [{
      id: 2, label: 'Middle', expand_in_tree: false,
      children: [{ id: 3, label: 'Leaf', expand_in_tree: false, children: [] }],
    }],
  }];
  const { container } = render(<App treeData={collapsedDeep} initialSelection={{}} />);
  expect(screen.queryByText('Middle')).toBeNull();
  fireEvent.click(container.querySelector('.clickable'), { altKey: true });
  expect(screen.getByText('Middle')).toBeInTheDocument();
  expect(screen.getByText('Leaf')).toBeInTheDocument();
});

test('checking root checks all descendants at every level', () => {
  render(<App treeData={deepTree} initialSelection={{}} />);
  const checkboxes = screen.getAllByRole('checkbox');
  fireEvent.click(checkboxes[0]);
  checkboxes.forEach(cb => expect(cb).toBeChecked());
});

test('unchecking a child after parent was checked makes parent indeterminate', () => {
  render(<App treeData={parentWithChildren} initialSelection={{}} />);
  const checkboxes = () => screen.getAllByRole('checkbox');
  // Check parent (checks all)
  fireEvent.click(checkboxes()[0]);
  // Uncheck Child A
  fireEvent.click(checkboxes()[1]);
  // Parent should not be checked
  expect(checkboxes()[0]).not.toBeChecked();
});

test('parent appears checked when all children are individually checked', () => {
  render(<App treeData={parentWithChildren} initialSelection={{}} />);
  const checkboxes = () => screen.getAllByRole('checkbox');
  fireEvent.click(checkboxes()[1]);
  fireEvent.click(checkboxes()[2]);
  expect(checkboxes()[0]).toBeChecked();
});

test('parent appears unchecked when all children are individually unchecked', () => {
  const allSelected = { '1': true, '2': true, '3': true };
  render(<App treeData={parentWithChildren} initialSelection={allSelected} />);
  const checkboxes = () => screen.getAllByRole('checkbox');
  fireEvent.click(checkboxes()[1]);
  fireEvent.click(checkboxes()[2]);
  expect(checkboxes()[0]).not.toBeChecked();
});
