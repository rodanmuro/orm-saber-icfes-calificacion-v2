import { Node, mergeAttributes } from '@tiptap/core';
import { NodeViewWrapper, ReactNodeViewRenderer } from '@tiptap/react';
import katex from 'katex';

function MathInlineNodeView({ node }) {
  const latex = node.attrs.latex || '';
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
