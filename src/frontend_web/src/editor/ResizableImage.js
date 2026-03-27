import { NodeSelection } from '@tiptap/pm/state';
import Image from '@tiptap/extension-image';

const MIN_IMAGE_WIDTH = 80;
const ALIGN_VALUES = new Set(['left', 'center', 'right']);
const HANDLE_DIRECTIONS = ['nw', 'ne', 'sw', 'se'];

function toPositiveNumber(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) return null;
  return Math.round(parsed);
}

function normalizeAlign(value) {
  if (typeof value !== 'string') return 'left';
  const normalized = value.trim().toLowerCase();
  return ALIGN_VALUES.has(normalized) ? normalized : 'left';
}

function widthFromDelta(startWidth, deltaX, direction) {
  const isWestHandle = direction.includes('w');
  const raw = isWestHandle ? startWidth - deltaX : startWidth + deltaX;
  return Math.max(MIN_IMAGE_WIDTH, Math.round(raw));
}

const ResizableImage = Image.extend({
  addAttributes() {
    return {
      ...(this.parent?.() || {}),
      width: {
        default: null,
        parseHTML: (element) => {
          const dataWidth = element.getAttribute('data-width');
          const widthAttr = element.getAttribute('width');
          return toPositiveNumber(dataWidth || widthAttr);
        },
        renderHTML: (attributes) => {
          const width = toPositiveNumber(attributes.width);
          if (!width) return {};
          return {
            'data-width': String(width),
            width: String(width),
            style: `width: ${width}px; height: auto;`,
          };
        },
      },
      align: {
        default: 'left',
        parseHTML: (element) => normalizeAlign(element.getAttribute('data-align')),
        renderHTML: (attributes) => ({
          'data-align': normalizeAlign(attributes.align),
        }),
      },
    };
  },

  addCommands() {
    return {
      ...(this.parent?.() || {}),
      setImageAlign:
        (align) =>
        ({ tr, state, dispatch }) => {
          const safeAlign = normalizeAlign(align);
          let targetPos = null;

          const selection = state.selection;
          if (selection instanceof NodeSelection && selection.node?.type?.name === this.name) {
            targetPos = selection.from;
          } else {
            const { from, to } = selection;
            state.doc.nodesBetween(from, to, (node, pos) => {
              if (node.type.name === this.name && targetPos === null) {
                targetPos = pos;
                return false;
              }
              return undefined;
            });
          }

          if (targetPos === null) return false;

          const node = state.doc.nodeAt(targetPos);
          if (!node) return false;

          if (dispatch) {
            tr.setNodeMarkup(targetPos, undefined, {
              ...node.attrs,
              align: safeAlign,
            });
            dispatch(tr);
          }

          return true;
        },
    };
  },

  addNodeView() {
    return ({ node, editor, getPos }) => {
      let currentNode = node;

      const dom = document.createElement('span');
      dom.className = 'resizable-image';
      dom.contentEditable = 'false';

      const image = document.createElement('img');
      image.draggable = false;
      dom.appendChild(image);

      const handles = HANDLE_DIRECTIONS.map((direction) => {
        const handle = document.createElement('span');
        handle.className = `resizable-image-handle resizable-image-handle-${direction}`;
        handle.dataset.direction = direction;
        dom.appendChild(handle);
        return handle;
      });

      const applyNodeAttrs = (targetNode) => {
        image.src = targetNode.attrs.src || '';
        image.alt = targetNode.attrs.alt || '';
        image.title = targetNode.attrs.title || '';

        const width = toPositiveNumber(targetNode.attrs.width);
        if (width) {
          image.style.width = `${width}px`;
        } else {
          image.style.width = '';
        }
        image.style.height = 'auto';

        const align = normalizeAlign(targetNode.attrs.align);
        dom.setAttribute('data-align', align);
      };

      const setNodeSelection = () => {
        if (typeof getPos !== 'function') return;
        const pos = getPos();
        if (typeof pos !== 'number') return;
        const tr = editor.state.tr.setSelection(NodeSelection.create(editor.state.doc, pos));
        editor.view.dispatch(tr);
      };

      applyNodeAttrs(currentNode);

      let resizing = false;
      let startX = 0;
      let startWidth = 0;
      let currentWidth = 0;
      let activeDirection = 'se';

      const onMouseMove = (event) => {
        if (!resizing) return;
        const deltaX = event.clientX - startX;
        currentWidth = widthFromDelta(startWidth, deltaX, activeDirection);
        image.style.width = `${currentWidth}px`;
      };

      const onMouseUp = () => {
        if (!resizing) return;
        resizing = false;
        document.removeEventListener('mousemove', onMouseMove);
        document.removeEventListener('mouseup', onMouseUp);

        if (typeof getPos !== 'function') return;
        const pos = getPos();
        if (typeof pos !== 'number') return;

        const tr = editor.state.tr.setNodeMarkup(pos, undefined, {
          ...currentNode.attrs,
          width: currentWidth,
        });
        editor.view.dispatch(tr);
      };

      const onImageMouseDown = () => {
        setNodeSelection();
      };

      const onHandleMouseDown = (event) => {
        event.preventDefault();
        event.stopPropagation();

        setNodeSelection();

        const direction = event.currentTarget?.dataset?.direction || 'se';
        activeDirection = HANDLE_DIRECTIONS.includes(direction) ? direction : 'se';

        resizing = true;
        startX = event.clientX;
        startWidth =
          Math.round(image.getBoundingClientRect().width) ||
          toPositiveNumber(currentNode.attrs.width) ||
          240;
        currentWidth = startWidth;

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
      };

      image.addEventListener('mousedown', onImageMouseDown);
      dom.addEventListener('mousedown', onImageMouseDown);
      handles.forEach((handle) => {
        handle.addEventListener('mousedown', onHandleMouseDown);
      });

      return {
        dom,
        update(updatedNode) {
          if (updatedNode.type.name !== currentNode.type.name) {
            return false;
          }
          currentNode = updatedNode;
          applyNodeAttrs(updatedNode);
          return true;
        },
        selectNode() {
          dom.classList.add('is-selected');
        },
        deselectNode() {
          dom.classList.remove('is-selected');
        },
        destroy() {
          image.removeEventListener('mousedown', onImageMouseDown);
          dom.removeEventListener('mousedown', onImageMouseDown);
          handles.forEach((handle) => {
            handle.removeEventListener('mousedown', onHandleMouseDown);
          });
          document.removeEventListener('mousemove', onMouseMove);
          document.removeEventListener('mouseup', onMouseUp);
        },
      };
    };
  },
});

export default ResizableImage;
