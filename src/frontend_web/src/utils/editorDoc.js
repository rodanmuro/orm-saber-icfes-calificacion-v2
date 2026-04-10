import { resolveAssetUrl } from '../api/assetsApi';

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
  const normalizeDocImageSrcs = (node) => {
    if (!node || typeof node !== 'object') return node;

    if (Array.isArray(node)) {
      return node.map(normalizeDocImageSrcs);
    }

    const out = { ...node };
    if (out.type === 'image') {
      const attrs = { ...(out.attrs || {}) };
      attrs.src = resolveAssetUrl(attrs.src || '');
      out.attrs = attrs;
    }
    if (Array.isArray(out.content)) {
      out.content = out.content.map(normalizeDocImageSrcs);
    }
    return out;
  };

  if (!value) return emptyDoc();
  if (typeof value === 'object') return normalizeDocImageSrcs(value);

  if (typeof value === 'string') {
    const raw = value.trim();
    if (!raw) return emptyDoc();
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object' && parsed.type === 'doc') {
        return normalizeDocImageSrcs(parsed);
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

export function docHasMeaningfulContent(doc) {
  if (!doc || typeof doc !== 'object') return false;

  function walk(node) {
    if (!node || typeof node !== 'object') return false;

    if (node.type === 'text' && typeof node.text === 'string' && node.text.trim().length > 0) {
      return true;
    }

    // Contenido no textual valido para banco de items.
    if (node.type === 'image') return true;
    if (node.type === 'math_inline' || node.type === 'mathInline' || node.type === 'math_block' || node.type === 'mathBlock') return true;

    if (Array.isArray(node.content)) {
      return node.content.some(walk);
    }
    return false;
  }

  return walk(doc);
}
