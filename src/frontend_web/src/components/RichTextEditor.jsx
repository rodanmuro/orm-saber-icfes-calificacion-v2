import { useEffect } from 'react';

import { EditorContent, useEditor } from '@tiptap/react';
import ResizableImage from '../editor/ResizableImage';
import StarterKit from '@tiptap/starter-kit';
import MathInline from '../editor/MathInline';
import { uploadEditorImage } from '../api/assetsApi';

const ALLOWED_IMAGE_TYPES = new Set(['image/png', 'image/jpeg', 'image/webp']);

function getImageFilesFromDataTransfer(dataTransfer) {
  if (!dataTransfer) return [];

  const fromItems = Array.from(dataTransfer.items || [])
    .filter((item) => item.kind === 'file')
    .map((item) => item.getAsFile())
    .filter((file) => file && ALLOWED_IMAGE_TYPES.has(file.type));

  if (fromItems.length > 0) {
    return fromItems;
  }

  return Array.from(dataTransfer.files || []).filter((file) => ALLOWED_IMAGE_TYPES.has(file.type));
}

export default function RichTextEditor({
  value,
  onChange,
  placeholder = '',
  minHeight = '92px',
  resizable = true,
}) {
  const insertUploadedImages = async (files, currentEditor) => {
    for (const file of files) {
      try {
        const upload = await uploadEditorImage(file);
        currentEditor.chain().focus().setImage({ src: upload.absoluteUrl, alt: file.name }).run();
      } catch (error) {
        // eslint-disable-next-line no-alert
        window.alert(`Error subiendo imagen: ${error.message}`);
      }
    }
  };

  const editor = useEditor({
    extensions: [StarterKit, ResizableImage, MathInline],
    content: value,
    editorProps: {
      attributes: {
        class: 'tiptap-editor',
        'data-placeholder': placeholder,
      },
      handlePaste: (view, event) => {
        const files = getImageFilesFromDataTransfer(event?.clipboardData);
        if (files.length === 0) {
          return false;
        }
        event.preventDefault();
        if (editor) {
          insertUploadedImages(files, editor);
        }
        return true;
      },
      handleDrop: (view, event) => {
        const files = getImageFilesFromDataTransfer(event?.dataTransfer);
        if (files.length === 0) {
          return false;
        }
        event.preventDefault();
        if (editor) {
          insertUploadedImages(files, editor);
        }
        return true;
      },
    },
    onUpdate({ editor: currentEditor }) {
      onChange(currentEditor.getJSON());
    },
  });

  const applyImageAlign = (align) => {
    if (!editor) return;
    const ok = editor.chain().focus().setImageAlign(align).run();
    if (!ok) {
      // eslint-disable-next-line no-alert
      window.alert('Selecciona primero una imagen para alinear.');
    }
  };

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
    <div
      className={`editor-shell ${resizable ? 'is-resizable' : ''}`}
      style={{ '--editor-min-height': minHeight }}
    >
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
            const latex = window.prompt('LaTeX (ej: \\frac{a+b}{c})');
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
        <button type="button" onClick={() => applyImageAlign('left')}>Img Izq</button>
        <button type="button" onClick={() => applyImageAlign('center')}>Img Centro</button>
        <button type="button" onClick={() => applyImageAlign('right')}>Img Der</button>
      </div>
      <div className="editor-hint">Tip: pega imagen con Ctrl+V o arrastra archivos al editor.</div>
      <EditorContent editor={editor} />
    </div>
  );
}
