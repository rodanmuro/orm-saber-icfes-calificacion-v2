import { useEffect } from 'react';

import { EditorContent, useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Table from '@tiptap/extension-table';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import TableRow from '@tiptap/extension-table-row';
import ResizableImage from '../editor/ResizableImage';
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
    extensions: [
      StarterKit,
      Table.configure({
        resizable: true,
        lastColumnResizable: true,
        allowTableNodeSelection: false,
      }),
      TableRow,
      TableHeader,
      TableCell,
      ResizableImage,
      MathInline,
    ],
    content: value,
    editable: true,
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
    if (editor.isFocused) return;
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
        <button
          type="button"
          onClick={() => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()}
        >
          Tabla
        </button>
        <button type="button" onClick={() => editor.chain().focus().toggleHeaderRow().run()}>
          Encabezado
        </button>
        <button type="button" onClick={() => editor.chain().focus().addRowBefore().run()}>Fila ↑</button>
        <button type="button" onClick={() => editor.chain().focus().addRowAfter().run()}>+Fila</button>
        <button type="button" onClick={() => editor.chain().focus().addColumnBefore().run()}>Col ←</button>
        <button type="button" onClick={() => editor.chain().focus().addColumnAfter().run()}>+Col</button>
        <button type="button" onClick={() => editor.chain().focus().deleteRow().run()}>-Fila</button>
        <button type="button" onClick={() => editor.chain().focus().deleteColumn().run()}>-Col</button>
        <button type="button" onClick={() => editor.chain().focus().deleteTable().run()}>-Tabla</button>
      </div>
      <div className="editor-hint">Tip: pega imagen con Ctrl+V o arrastra archivos al editor. Para editar tabla, haz clic dentro de una celda. Para escalar tabla, arrastra el borde entre columnas.</div>
      <EditorContent editor={editor} />
    </div>
  );
}
