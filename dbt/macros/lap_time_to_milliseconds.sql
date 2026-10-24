{% macro lap_time_to_milliseconds(column_name) -%}
case
    when {{ column_name }} is null then null
    when regexp_like({{ column_name }}, '^[0-9]+:[0-9]{2}\.[0-9]{3}$') then
        round(
            try_to_number(split_part({{ column_name }}, ':', 1)) * 60000
            + try_to_double(split_part({{ column_name }}, ':', 2)) * 1000,
            0
        )::number(10, 0)
    else null
end
{%- endmacro %}
