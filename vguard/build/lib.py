"""Small helpers for editing the V-Guard decks in place while keeping their formatting."""
import copy
from pptx.util import Emu
from pptx.dml.color import RGBColor

E = 914400


def shp(slide, sid):
    for sh in _walk(slide.shapes):
        if sh.shape_id == sid:
            return sh
    raise KeyError(f"shape {sid} not found")


def _walk(shapes):
    for sh in shapes:
        yield sh
        if sh.shape_type == 6:
            yield from _walk(sh.shapes)


def set_paras(sh, texts):
    """texts: list per paragraph; each item a str (one run) or list of run strings.
    Keeps the formatting of existing paragraphs/runs; clones the last one when more are needed."""
    tf = sh.text_frame
    body = tf._txBody
    while len(tf.paragraphs) < len(texts):
        body.append(copy.deepcopy(tf.paragraphs[-1]._p))
    while len(tf.paragraphs) > len(texts):
        p = tf.paragraphs[-1]._p
        p.getparent().remove(p)
    for para, t in zip(tf.paragraphs, texts):
        if isinstance(t, str):
            t = [t]
        if not para.runs:
            para.add_run()
        while len(para.runs) < len(t):
            para.runs[-1]._r.addnext(copy.deepcopy(para.runs[-1]._r))
        while len(para.runs) > len(t):
            r = para.runs[-1]._r
            r.getparent().remove(r)
        for r, tt in zip(para.runs, t):
            r.text = tt


def pos(sh, x=None, y=None, w=None, h=None):
    if x is not None:
        sh.left = Emu(int(round(x * E)))
    if y is not None:
        sh.top = Emu(int(round(y * E)))
    if w is not None:
        sh.width = Emu(int(round(w * E)))
    if h is not None:
        sh.height = Emu(int(round(h * E)))


def fill(sh, hexrgb):
    sh.fill.solid()
    sh.fill.fore_color.rgb = RGBColor.from_string(hexrgb)


def _max_id(slide):
    ids = [int(e.get("id")) for e in slide.shapes._spTree.iter() if e.tag.endswith("}cNvPr")]
    return max(ids) if ids else 1


def clone(slide, src, **kw):
    el = copy.deepcopy(src._element)
    slide.shapes._spTree.append(el)
    nid = _max_id(slide) + 1
    for e in el.iter():
        if e.tag.endswith("}cNvPr"):
            e.set("id", str(nid))
            e.set("name", f"{e.get('name').split(' ')[0]} {nid}")
            break
    new = [s for s in slide.shapes if s._element is el][0]
    if any(k in kw for k in ("x", "y", "w", "h")):
        pos(new, kw.get("x"), kw.get("y"), kw.get("w"), kw.get("h"))
    if "text" in kw:
        set_paras(new, kw["text"])
    if "fill" in kw:
        fill(new, kw["fill"])
    return new


def delete(sh):
    el = sh._element
    el.getparent().remove(el)


def copy_slide_shapes(prs, src_slide):
    """Append a new slide with the same layout and a deep copy of the source's shapes.
    Only for slides without charts or pictures (no relationships to copy)."""
    new = prs.slides.add_slide(src_slide.slide_layout)
    tree = new.shapes._spTree
    for el in list(tree):
        if el.tag.endswith("}sp") or el.tag.endswith("}grpSp") or el.tag.endswith("}cxnSp") or el.tag.endswith("}graphicFrame") or el.tag.endswith("}pic"):
            tree.remove(el)
    for el in src_slide.shapes._spTree:
        if el.tag.endswith(("}sp", "}grpSp", "}cxnSp", "}graphicFrame", "}pic")):
            tree.append(copy.deepcopy(el))
    return new


def move_slide(prs, old_index, new_index):
    lst = prs.slides._sldIdLst
    items = list(lst)
    el = items[old_index]
    lst.remove(el)
    lst.insert(new_index, el)


def waterfall(slide, bars, *, tmpl_rect, tmpl_val, tmpl_cat, tmpl_conn, x0, step, bw, base_y, scale,
              val_w=None, cat_w=None, cat_y=None, cat_h=0.60, colors=None):
    """bars: list of (category label, value, kind) with kind in {'total','inc'}; value in data units.
    Builds rectangles, value labels, category labels and connectors from template shapes."""
    colors = colors or {}
    level = 0.0
    made = []
    val_w = val_w or step
    cat_w = cat_w or step
    for i, (cat, val, kind, label) in enumerate(bars):
        bx = x0 + i * step
        if kind == "total":
            top = base_y - val * scale
            h = val * scale
            level = val
        else:
            h = val * scale
            top = base_y - (level + val) * scale
            level = level + val
        col = colors.get(i, "D9730D" if kind == "inc" else "012169")
        r = clone(slide, tmpl_rect, x=bx, y=top, w=bw, h=max(h, 0.02), fill=col)
        cx = bx + bw / 2
        v = clone(slide, tmpl_val, x=cx - val_w / 2, y=top - 0.24, w=val_w, h=0.22, text=[label])
        c = clone(slide, tmpl_cat, x=cx - cat_w / 2, y=cat_y if cat_y is not None else base_y + 0.05, w=cat_w, h=cat_h, text=[cat])
        made += [r, v, c]
        if i < len(bars) - 1:
            cn = clone(slide, tmpl_conn, x=bx + bw, y=top, w=step - bw, h=0)
            made.append(cn)
    return made


def page_numbers(prs, first=2):
    for i, s in enumerate(prs.slides, 1):
        if i < first:
            continue
        for sh in s.shapes:
            if sh.has_text_frame and sh.left > Emu(int(12.2 * E)) and sh.top > Emu(int(7.0 * E)):
                t = sh.text_frame.text.strip()
                if t.isdigit():
                    set_paras(sh, [str(i)])
