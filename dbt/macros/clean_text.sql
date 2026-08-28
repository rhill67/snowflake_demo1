{% macro clean_text(column_name) -%}
    upper(trim({{ column_name }}))
{%- endmacro %}
