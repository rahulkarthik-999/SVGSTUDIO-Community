"""
SVG Optimizer - Core Passes

All optimization passes are registered via the PassRegistry.
Each pass receives an OptimizationContext and returns a PassResult.
"""

import re
import xml.etree.ElementTree as ET
from typing import Set, Dict

from ..core.engine import (
    PassRegistry, PassResult, OptimizationContext, SVGSerializer
)


# Elements to remove completely
HIDDEN_ELEMENTS = {'metadata', 'desc', 'title'}

# Editor-specific attributes to remove
EDITOR_ATTRS = {
    'inkscape:version', 'inkscape:generator', 'inkscape:label',
    'sodipodi:docname', 'sodipodi:version',
    'sketch:type',
    'data-name', 'data-layer',
}

# Safe attributes that can be removed if empty
EMPTY_SAFE_ATTRS = {'class', 'style', 'id', 'name', 'title', 'data-id'}


@PassRegistry.register(
    "remove_xml_declaration",
    "Remove <?xml?> declaration from SVG",
    default_enabled=True
)
def remove_xml_declaration(ctx: OptimizationContext) -> PassResult:
    """Remove XML declaration."""
    result = re.sub(r'<\?xml[^>]*\?>', '', ctx.current_content, flags=re.IGNORECASE)
    
    removed = len(ctx.current_content) - len(result)
    return PassResult(
        success=True,
        content=result,
        stats_delta={"removed_elements": 1 if removed > 0 else 0}
    )


@PassRegistry.register(
    "remove_comments",
    "Remove HTML/XML comments",
    default_enabled=True
)
def remove_comments(ctx: OptimizationContext) -> PassResult:
    """Remove comments."""
    pattern = r'<!--.*?-->'
    matches = re.findall(pattern, ctx.current_content, re.DOTALL)
    result = re.sub(pattern, '', ctx.current_content, flags=re.DOTALL)
    
    return PassResult(
        success=True,
        content=result,
        stats_delta={"removed_comments": len(matches)}
    )


@PassRegistry.register(
    "remove_namespaces",
    "Remove editor-specific namespace declarations",
    default_enabled=False
)
def remove_namespaces(ctx: OptimizationContext) -> PassResult:
    """Remove editor namespace declarations and attributes."""
    result = ctx.current_content
    removed_count = 0
    
    # Remove xmlns declarations for editor namespaces
    for ns_uri, prefix in SVGSerializer.EDITOR_NAMESPACES.items():
        # Remove xmlns:prefix="..."
        pattern = rf'\s*xmlns:{prefix}="[^"]*"'
        matches = re.findall(pattern, result)
        removed_count += len(matches)
        result = re.sub(pattern, '', result)
        
        # Remove attributes with this prefix
        pattern = rf'\s*{prefix}:[a-zA-Z0-9_-]+="[^"]*"'
        matches = re.findall(pattern, result)
        removed_count += len(matches)
        result = re.sub(pattern, '', result)
    
    return PassResult(
        success=True,
        content=result,
        stats_delta={"removed_namespaces": removed_count}
    )


@PassRegistry.register(
    "remove_editor_namespaces",
    "Remove editor-specific namespace declarations",
    default_enabled=True
)
def remove_editor_namespaces(ctx: OptimizationContext) -> PassResult:
    """Backwards-compatible alias for remove_namespaces."""
    return remove_namespaces(ctx)


@PassRegistry.register(
    "remove_metadata",
    "Remove <metadata> elements",
    default_enabled=True
)
def remove_metadata(ctx: OptimizationContext) -> PassResult:
    """Remove metadata elements."""
    # Use regex first - more reliable for metadata removal
    pattern = r'<metadata[^>]*>.*?</metadata>'
    matches = re.findall(pattern, ctx.current_content, re.DOTALL | re.IGNORECASE)
    result = re.sub(pattern, '', ctx.current_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Also try ElementTree approach for any remaining metadata
    removed = len(matches)
    try:
        # Strip XML declaration for parsing
        parse_content = re.sub(r'<\?xml[^>]*\?>', '', result)
        root = ET.fromstring(parse_content.strip())
        
        for meta in list(root.iter()):
            if SVGSerializer.clean_tag(meta.tag) == 'metadata':
                parent = None
                for p in root.iter():
                    if meta in list(p):
                        parent = p
                        break
                if parent is not None:
                    parent.remove(meta)
                    removed += 1
        
        result = SVGSerializer.serialize(root)
    except ET.ParseError:
        pass
    
    return PassResult(
        success=True,
        content=result,
        stats_delta={"removed_elements": removed}
    )


@PassRegistry.register(
    "remove_hidden_elements",
    "Remove hidden/non-rendering elements (metadata, desc, title)",
    default_enabled=True
)
def remove_hidden_elements(ctx: OptimizationContext) -> PassResult:
    """Remove hidden elements."""
    # Use regex first for reliable removal
    result = ctx.current_content
    removed = 0
    
    for tag in HIDDEN_ELEMENTS:
        pattern = rf'<{tag}[^>]*>.*?</{tag}>'
        matches = re.findall(pattern, result, re.DOTALL | re.IGNORECASE)
        removed += len(matches)
        result = re.sub(pattern, '', result, flags=re.DOTALL | re.IGNORECASE)
    
    # Also try ElementTree approach for any remaining hidden elements
    try:
        parse_content = re.sub(r'<\?xml[^>]*\?>', '', result)
        root = ET.fromstring(parse_content.strip())
        
        for tag in HIDDEN_ELEMENTS:
            for elem in list(root.iter()):
                if SVGSerializer.clean_tag(elem.tag) == tag:
                    parent = None
                    for p in root.iter():
                        if elem in list(p):
                            parent = p
                            break
                    if parent is not None:
                        parent.remove(elem)
                        removed += 1
        
        # Check for display:none or visibility:hidden
        for elem in list(root.iter()):
            style = elem.get('style', '')
            if 'display:none' in style.replace(' ', '') or \
               'visibility:hidden' in style.replace(' ', ''):
                parent = None
                for p in root.iter():
                    if elem in list(p):
                        parent = p
                        break
                if parent is not None:
                    parent.remove(elem)
                    removed += 1
        
        result = SVGSerializer.serialize(root)
    except ET.ParseError:
        pass
    
    return PassResult(
        success=True,
        content=result,
        stats_delta={"removed_elements": removed}
    )


@PassRegistry.register(
    "remove_empty_attributes",
    "Remove empty attributes and editor-specific attributes",
    default_enabled=True
)
def remove_empty_attributes(ctx: OptimizationContext) -> PassResult:
    """Remove empty and editor-specific attributes."""
    # Use regex first for reliable removal of empty attributes
    result = re.sub(r'\s+\w+=""', '', ctx.current_content)
    removed = 0
    
    # Count removed empty attributes
    for match in re.finditer(r'\w+=""', ctx.current_content):
        removed += 1
    
    # Also try ElementTree approach for editor-specific attributes
    try:
        parse_content = re.sub(r'<\?xml[^>]*\?>', '', result)
        root = ET.fromstring(parse_content.strip())
        
        for elem in root.iter():
            attrs_to_remove = []
            for attr, value in list(elem.attrib.items()):
                # Remove empty attributes
                if value == '' or value is None:
                    attrs_to_remove.append(attr)
                # Remove editor-specific attributes
                elif any(attr.startswith(p) for p in EDITOR_ATTRS):
                    attrs_to_remove.append(attr)
            
            for attr in attrs_to_remove:
                del elem.attrib[attr]
                removed += 1
        
        result = SVGSerializer.serialize(root)
    except ET.ParseError:
        pass
    
    return PassResult(
        success=True,
        content=result,
        stats_delta={"removed_attributes": removed}
    )


@PassRegistry.register(
    "trim_trailing_zeros",
    "Trim trailing zeros from decimal numbers (1.000 → 1)",
    default_enabled=True
)
def trim_trailing_zeros(ctx: OptimizationContext) -> PassResult:
    """Trim trailing zeros from numbers."""
    def trim_number(match):
        num_str = match.group(0)
        try:
            num = float(num_str)
            if num == int(num):
                return str(int(num))
            else:
                formatted = f"{num:.10f}".rstrip('0').rstrip('.')
                return formatted
        except ValueError:
            return num_str
    
    # Match numbers in attribute values
    result = re.sub(
        r'(?<=["\s:,])(-?\d+\.?\d*)(?=["\s\),;:])',
        trim_number,
        ctx.current_content
    )
    
    return PassResult(success=True, content=result)


@PassRegistry.register(
    "collapse_whitespace",
    "Collapse whitespace between tags",
    default_enabled=True
)
def collapse_whitespace(ctx: OptimizationContext) -> PassResult:
    """Collapse whitespace."""
    result = re.sub(r'>\s+<', '><', ctx.current_content)
    result = result.strip()
    return PassResult(success=True, content=result)


@PassRegistry.register(
    "remove_unused_ids",
    "Remove unused ID definitions (preserves referenced IDs)",
    default_enabled=True
)
def remove_unused_ids(ctx: OptimizationContext) -> PassResult:
    """Remove unused IDs while preserving referenced ones."""
    try:
        root = ET.fromstring(ctx.current_content)
        
        # Collect all defined IDs
        defined_ids: Set[str] = set()
        id_elements: Dict[str, ET.Element] = {}
        
        for elem in root.iter():
            elem_id = elem.get('id')
            if elem_id:
                defined_ids.add(elem_id)
                id_elements[elem_id] = elem
        
        # Collect all referenced IDs
        referenced_ids: Set[str] = set()
        
        for elem in root.iter():
            # Check href attributes
            for attr in ['href', '{http://www.w3.org/1999/xlink}href']:
                href = elem.get(attr, '')
                if href.startswith('#'):
                    referenced_ids.add(href[1:])
            
            # Check style attributes for url() references
            style = elem.get('style', '')
            for match in re.finditer(r'url\(#([^)]+)\)', style):
                referenced_ids.add(match.group(1))
            
            # Check individual style properties
            for attr in ['fill', 'stroke', 'clip-path', 'mask', 'filter', 
                        'marker-start', 'marker-mid', 'marker-end']:
                value = elem.get(attr, '')
                if value.startswith('url(#') and value.endswith(')'):
                    referenced_ids.add(value[5:-1])
        
        # Store for context
        ctx.defined_ids = defined_ids
        ctx.referenced_ids = referenced_ids
        
        # Remove unused IDs
        unused_ids = defined_ids - referenced_ids
        removed = 0
        
        for unused_id in unused_ids:
            elem = id_elements.get(unused_id)
            if elem is not None:
                del elem.attrib['id']
                removed += 1
        
        result = SVGSerializer.serialize(root)
        return PassResult(
            success=True,
            content=result,
            stats_delta={"removed_ids": removed}
        )
    except ET.ParseError:
        return PassResult(success=True, content=ctx.current_content)


@PassRegistry.register(
    "round_decimals",
    "Round decimal numbers to 3 places",
    default_enabled=True
)
def round_decimals(ctx: OptimizationContext) -> PassResult:
    """Round decimals to specified precision."""
    def round_number(match):
        num_str = match.group(0)
        try:
            num = float(num_str)
            rounded = round(num, 3)
            if rounded == int(rounded):
                return str(int(rounded))
            return str(rounded)
        except ValueError:
            return num_str
    
    result = re.sub(
        r'(?<=["\s:,])(-?\d+\.\d+)(?=["\s\),;:])',
        round_number,
        ctx.current_content
    )
    
    return PassResult(success=True, content=result)


@PassRegistry.register(
    "collapse_groups",
    "Collapse trivial <g> elements",
    default_enabled=False
)
def collapse_groups(ctx: OptimizationContext) -> PassResult:
    """Collapse groups with no meaningful attributes."""
    try:
        root = ET.fromstring(ctx.current_content)
        changed = True
        removed = 0
        
        while changed:
            changed = False
            for g in root.findall('.//{*}g'):
                children = [c for c in g if not isinstance(c, type(ET.Comment()))]
                if len(children) == 1:
                    # Check if group has no important attributes
                    important_attrs = {'transform', 'id', 'class', 'style'}
                    if not any(attr in g.attrib for attr in important_attrs):
                        child = children[0]
                        child.attrib.update(g.attrib)
                        
                        # Replace group with child
                        parent = None
                        for p in root.iter():
                            if g in list(p):
                                parent = p
                                break
                        
                        if parent is not None:
                            idx = list(parent).index(g)
                            parent.remove(g)
                            parent.insert(idx, child)
                            changed = True
                            removed += 1
        
        result = SVGSerializer.serialize(root)
        return PassResult(
            success=True,
            content=result,
            stats_delta={"removed_elements": removed}
        )
    except ET.ParseError:
        return PassResult(success=True, content=ctx.current_content)


@PassRegistry.register(
    "sort_attributes",
    "Sort attributes alphabetically for consistency",
    default_enabled=False
)
def sort_attributes(ctx: OptimizationContext) -> PassResult:
    """Sort attributes alphabetically."""
    try:
        root = ET.fromstring(ctx.current_content)
        
        for elem in root.iter():
            if len(elem.attrib) > 1:
                sorted_attrib = dict(sorted(elem.attrib.items()))
                elem.attrib.clear()
                elem.attrib.update(sorted_attrib)
        
        result = SVGSerializer.serialize(root)
        return PassResult(success=True, content=result)
    except ET.ParseError:
        return PassResult(success=True, content=ctx.current_content)
