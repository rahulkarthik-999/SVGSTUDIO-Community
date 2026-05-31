"""
SVG Optimizer Core - Pass Engine Architecture

Provides:
- PassManager: Orchestrates optimization passes
- OptimizationContext: Holds state during optimization
- PassRegistry: Registers and discovers passes
- Serializer: Clean SVG serialization without namespace pollution
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Callable
from xml.etree import ElementTree as ET


@dataclass
class OptimizationContext:
    """Holds state during SVG optimization."""
    original_content: str
    current_content: str = ""
    stats: Dict[str, Any] = field(default_factory=lambda: {
        "original_size": 0,
        "optimized_size": 0,
        "removed_elements": 0,
        "removed_attributes": 0,
        "removed_comments": 0,
        "removed_ids": 0,
        "removed_namespaces": 0,
    })
    defined_ids: Set[str] = field(default_factory=set)
    referenced_ids: Set[str] = field(default_factory=set)
    id_elements: Dict[str, Any] = field(default_factory=dict)
    preserved_ids: Set[str] = field(default_factory=set)  # IDs that must be kept
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.current_content = self.original_content
        self.stats["original_size"] = len(self.original_content.encode('utf-8'))


@dataclass
class PassResult:
    """Result of a single optimization pass."""
    success: bool
    content: str
    stats_delta: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class PassRegistry:
    """Registry for optimization passes."""
    
    _passes: Dict[str, Callable] = {}
    _metadata: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register(cls, name: str, description: str = "", default_enabled: bool = True):
        """Decorator to register an optimization pass."""
        def decorator(func: Callable) -> Callable:
            cls._passes[name] = func
            cls._metadata[name] = {
                "description": description,
                "default_enabled": default_enabled,
            }
            return func
        return decorator
    
    @classmethod
    def get_pass(cls, name: str) -> Optional[Callable]:
        """Get a pass by name."""
        return cls._passes.get(name)
    
    @classmethod
    def get_all_passes(cls) -> List[str]:
        """Get all registered pass names."""
        return list(cls._passes.keys())
    
    @classmethod
    def get_metadata(cls, name: str) -> Dict[str, Any]:
        """Get metadata for a pass."""
        return cls._metadata.get(name, {})
    
    @classmethod
    def get_default_passes(cls) -> List[str]:
        """Get all passes that are enabled by default."""
        return [
            name for name, meta in cls._metadata.items()
            if meta.get("default_enabled", True)
        ]


class PassManager:
    """Manages and executes optimization passes."""
    
    def __init__(self, passes: Optional[List[str]] = None):
        """
        Initialize the pass manager.
        
        Args:
            passes: List of pass names to apply. If None, uses defaults.
        """
        if passes is None:
            self.passes = PassRegistry.get_default_passes()
        else:
            self.passes = passes
        self.results: List[PassResult] = []
    
    def execute(self, context: OptimizationContext) -> OptimizationContext:
        """
        Execute all configured passes on the context.
        
        Args:
            context: The optimization context.
            
        Returns:
            The modified context.
        """
        for pass_name in self.passes:
            pass_func = PassRegistry.get_pass(pass_name)
            if pass_func is None:
                context.warnings.append(f"Unknown pass: {pass_name}")
                continue
            
            try:
                result = pass_func(context)
                self.results.append(result)
                
                if result.success:
                    context.current_content = result.content
                    # Merge stats
                    for key, value in result.stats_delta.items():
                        if key in context.stats:
                            context.stats[key] += value
                        else:
                            context.stats[key] = value
                    
                    context.errors.extend(result.errors)
                    context.warnings.extend(result.warnings)
                else:
                    context.errors.extend(result.errors)
            except Exception as e:
                context.errors.append(f"Pass {pass_name} failed: {str(e)}")
                self.results.append(PassResult(
                    success=False,
                    content=context.current_content,
                    errors=[str(e)]
                ))
        
        # Finalize stats
        context.stats["optimized_size"] = len(
            context.current_content.encode('utf-8')
        )
        
        return context


class SVGSerializer:
    """Clean SVG serialization without namespace pollution."""
    
    SVG_NS = "http://www.w3.org/2000/svg"
    XLINK_NS = "http://www.w3.org/1999/xlink"
    
    # Namespaces to remove
    EDITOR_NAMESPACES = {
        "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd": "sodipodi",
        "http://inkscape.sourceforge.net/DTD/sodipodi-0.dtd": "inkscape",
        "http://www.inkscape.org/namespaces/inkscape": "inkscape",
        "http://schemas.microsoft.com/visio/2003/core": "visio",
        "http://www.adobe.com/namespaces/AdobeSVGViewerExtensions/3.0/": "adobe",
        "http://www.bohemiancoding.com/sketch/ns": "sketch",
        "http://purl.org/dc/elements/1.1/": "dc",
    }
    
    @classmethod
    def clean_tag(cls, tag: str) -> str:
        """Remove namespace prefix from tag."""
        if '}' in tag:
            return tag.split('}', 1)[1]
        return tag
    
    @classmethod
    def clean_attrib(cls, attrib: Dict[str, str]) -> Dict[str, str]:
        """Clean attribute names and filter editor-specific attributes."""
        cleaned = {}
        editor_attrs = {
            'inkscape:', 'sodipodi:', 'sketch:', 'adobe:', 'visio:',
            'data-name', 'data-layer'
        }
        
        for key, value in attrib.items():
            # Skip editor-specific attributes
            if any(key.startswith(p) or key == p.rstrip(':') 
                   for p in editor_attrs):
                continue
            
            # Clean namespace from attribute name
            if '}' in key:
                clean_key = key.split('}', 1)[1]
            else:
                clean_key = key
            
            # Skip xmlns declarations for editor namespaces
            if clean_key.startswith('xmlns:'):
                prefix = clean_key[6:]
                if prefix in cls.EDITOR_NAMESPACES.values():
                    continue
            
            cleaned[clean_key] = value
        
        return cleaned
    
    @classmethod
    def serialize(cls, root: ET.Element, xml_declaration: bool = False) -> str:
        """
        Serialize an ElementTree element to clean SVG string.
        
        Args:
            root: The root element.
            xml_declaration: Whether to include XML declaration.
            
        Returns:
            Clean SVG string.
        """
        def elem_to_string(elem: ET.Element, level: int = 0) -> str:
            tag = cls.clean_tag(elem.tag)
            attrib = cls.clean_attrib(elem.attrib)
            
            # Build opening tag
            if attrib:
                attrs = ' '.join(
                    f'{k}="{cls._escape_attr(v)}"' 
                    for k, v in sorted(attrib.items())
                )
                open_tag = f"<{tag} {attrs}>"
            else:
                open_tag = f"<{tag}>"
            
            # Get text content
            text = (elem.text or '').strip()
            tail = (elem.tail or '').strip()
            
            # Children - skip comments (ET.Comment is a function, comments have callable tag)
            children = [c for c in elem if not callable(c.tag)]
            
            if not text and not children:
                # Self-closing tag
                result = open_tag.replace('>', '/>')
            else:
                result = open_tag
                if text:
                    result += text
                
                for child in children:
                    result += elem_to_string(child, level + 1)
                
                result += f"</{tag}>"
            
            # Add tail
            if tail and level > 0:
                result += tail
            
            return result
        
        # Handle comments separately (comments have callable tag)
        comments = []
        for elem in root:
            if callable(elem.tag):
                comments.append(f"<!--{elem.text}-->")
        
        svg_str = elem_to_string(root)
        
        # Insert comments after root tag
        if comments:
            parts = svg_str.split('>', 1)
            if len(parts) == 2:
                svg_str = parts[0] + '>' + ''.join(comments) + parts[1]
        
        if xml_declaration:
            svg_str = '<?xml version="1.0" encoding="UTF-8"?>' + svg_str
        
        return svg_str
    
    @classmethod
    def _escape_attr(cls, value: str) -> str:
        """Escape special characters in attribute values."""
        return (value
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))


# Import passes to register them - use absolute import
from svg_optimizer.passes import basic  # noqa: F401


