"""
模板工具 - 简化版本，用于Replit部署
"""

from jinja2 import Template

def render_template_string(template_str, **kwargs):
    """渲染模板字符串"""
    template = Template(template_str)
    return template.render(**kwargs)