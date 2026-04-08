import { useEffect } from 'react';
import { EditorContent, useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Table from '@tiptap/extension-table';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import TableRow from '@tiptap/extension-table-row';
import ResizableImage from '../editor/ResizableImage';
import MathInline from '../editor/MathInline';

export default function RichDocPreview({ value }) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Table.configure({
        resizable: false,
        lastColumnResizable: false,
      }),
      TableRow,
      TableHeader,
      TableCell,
      ResizableImage,
      MathInline,
    ],
    content: value,
    editable: false,
    editorProps: {
      attributes: {
        class: 'tiptap-editor',
      },
    },
  });

  useEffect(() => {
    if (!editor) return;
    const currentRaw = JSON.stringify(editor.getJSON());
    const nextRaw = JSON.stringify(value);
    if (currentRaw !== nextRaw) {
      editor.commands.setContent(value, false);
    }
  }, [editor, value]);

  if (!editor) return null;

  return (
    <div className="editor-shell rich-doc-preview">
      <EditorContent editor={editor} />
    </div>
  );
}

