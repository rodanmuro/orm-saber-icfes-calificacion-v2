import { Node, mergeAttributes } from '@tiptap/core';
import { NodeViewWrapper, ReactNodeViewRenderer } from '@tiptap/react';
import katex from 'katex';

function normalizeLatex(input) {
  let value = (input || '').trim();
  if (!value) return '';

  // Remove common math delimiters accidentally included by LLM output.
  if (value.startsWith('$$') && value.endsWith('$$') && value.length > 4) {
    value = value.slice(2, -2).trim();
  } else if (value.startsWith('$') && value.endsWith('$') && value.length > 2) {
    value = value.slice(1, -1).trim();
  }

  // Escape currency dollars not already escaped.
  value = value.replace(/(^|[^\\])\$/g, '$1\\$');
  return value;
}

function MathInlineNodeView({ node, updateAttributes, selected }) {
  const latex = normalizeLatex(node.attrs.latex || '');
  const rendered = katex.renderToString(latex || '\\text{?}', {
    throwOnError: false,
    strict: 'ignore',
  });

  const openLatexEditor = (event) => {
    event.preventDefault();
    event.stopPropagation();

    const next = window.prompt('Editar LaTeX', latex || '');
    if (next === null) return;

    const normalized = normalizeLatex(next);
    if (!normalized) return;

    updateAttributes({ latex: normalized });
  };

  const handleMouseDown = (event) => {
    if (event.detail === 2) {
      openLatexEditor(event);
    }
  };

  return (
    <NodeViewWrapper
      as="span"
      className={`math-inline ${selected ? 'is-selected' : ''}`}
      contentEditable={false}
      title="Doble clic para editar ecuacion"
      onDoubleClick={openLatexEditor}
      onMouseDown={handleMouseDown}
    >
      <span
        onDoubleClick={openLatexEditor}
        onMouseDown={handleMouseDown}
        dangerouslySetInnerHTML={{ __html: rendered }}
      />
    </NodeViewWrapper>
  );
}

const MathInline = Node.create({
  name: 'mathInline',
  group: 'inline',
  inline: true,
  atom: true,

  addAttributes() {
    return {
      latex: {
        default: '',
      },
    };
  },

  parseHTML() {
    return [{ tag: 'span[data-math-inline]' }];
  },

  renderHTML({ HTMLAttributes }) {
    return ['span', mergeAttributes(HTMLAttributes, { 'data-math-inline': 'true' })];
  },

  addCommands() {
    return {
      setMathInline:
        (latex) =>
        ({ commands }) => {
          return commands.insertContent({ type: this.name, attrs: { latex } });
        },
    };
  },

  addNodeView() {
    return ReactNodeViewRenderer(MathInlineNodeView);
  },
});

export default MathInline;
