export function emptyDoc() {
  return {
    type: 'doc',
    content: [{ type: 'paragraph' }],
  };
}

export function textToDoc(text) {
  const safeText = (text || '').trim();
  if (!safeText) return emptyDoc();
  return {
    type: 'doc',
    content: [{ type: 'paragraph', content: [{ type: 'text', text: safeText }] }],
  };
}

export function storageToDoc(value) {
  if (!value) return emptyDoc();
  if (typeof value === 'object') return value;

  if (typeof value === 'string') {
    const raw = value.trim();
    if (!raw) return emptyDoc();
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object' && parsed.type === 'doc') {
        return parsed;
      }
    } catch {
      // fallback to plain text doc
    }
    return textToDoc(raw);
  }

  return emptyDoc();
}

export function docToStorage(doc) {
  return JSON.stringify(doc || emptyDoc());
}

export function docToPlainText(doc) {
  if (!doc || typeof doc !== 'object') return '';
  const chunks = [];

  function walk(node) {
    if (!node || typeof node !== 'object') return;
    if (node.type === 'text' && typeof node.text === 'string') {
      chunks.push(node.text);
    }
    if (Array.isArray(node.content)) {
      node.content.forEach(walk);
      if (node.type === 'paragraph') chunks.push(' ');
    }
  }

  walk(doc);
  return chunks.join('').replace(/\s+/g, ' ').trim();
}
