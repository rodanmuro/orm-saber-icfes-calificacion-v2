import { useEffect } from 'react';

import { EditorContent, useEditor } from '@tiptap/react';
import Image from '@tiptap/extension-image';
import StarterKit from '@tiptap/starter-kit';
import MathInline from '../editor/MathInline';
import { uploadEditorImage } from '../api/assetsApi';

export default function RichTextEditor({ value, onChange, placeholder = '' }) {
  const editor = useEditor({
    extensions: [StarterKit, Image, MathInline],
    content: value,
    editorProps: {
      attributes: {
        class: 'tiptap-editor',
        'data-placeholder': placeholder,
      },
    },
    onUpdate({ editor: currentEditor }) {
      onChange(currentEditor.getJSON());
    },
  });

  useEffect(() => {
    if (!editor) return;
    const current = editor.getJSON();
    const currentRaw = JSON.stringify(current);
    const nextRaw = JSON.stringify(value);
    if (currentRaw !== nextRaw) {
      editor.commands.setContent(value, false);
    }
  }, [editor, value]);

  if (!editor) return null;

  return (
    <div className="editor-shell">
      <div className="editor-toolbar">
        <button type="button" onClick={() => editor.chain().focus().toggleBold().run()}>
          B
        </button>
        <button type="button" onClick={() => editor.chain().focus().toggleItalic().run()}>
          I
        </button>
        <button type="button" onClick={() => editor.chain().focus().toggleBulletList().run()}>
          Lista
        </button>
        <button type="button" onClick={() => editor.chain().focus().setParagraph().run()}>
          P
        </button>
        <button
          type="button"
          onClick={() => {
            const latex = window.prompt('LaTeX (ej: \\\\frac{a+b}{c})');
            if (!latex) return;
            editor.chain().focus().setMathInline(latex).run();
          }}
        >
          fx
        </button>
        <label className="image-upload-btn">
          Imagen
          <input
            type="file"
            accept="image/png,image/jpeg,image/webp"
            onChange={async (event) => {
              const file = event.target.files?.[0];
              event.target.value = '';
              if (!file) return;
              try {
                const upload = await uploadEditorImage(file);
                editor.chain().focus().setImage({ src: upload.absoluteUrl, alt: file.name }).run();
              } catch (error) {
                // eslint-disable-next-line no-alert
                window.alert(`Error subiendo imagen: ${error.message}`);
              }
            }}
          />
        </label>
      </div>
      <EditorContent editor={editor} />
    </div>
  );
}
