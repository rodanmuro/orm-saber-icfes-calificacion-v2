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

function MathInlineNodeView({ node }) {
  const latex = normalizeLatex(node.attrs.latex || '');
  const rendered = katex.renderToString(latex || '\\text{?}', {
    throwOnError: false,
    strict: 'ignore',
  });

  return (
    <NodeViewWrapper as="span" className="math-inline" contentEditable={false}>
      <span dangerouslySetInnerHTML={{ __html: rendered }} />
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
