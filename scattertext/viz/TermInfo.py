import html

import pandas as pd

def get_tooltip_js_function(plot_df, tooltip_column_names, tooltip_columns):
    if len(tooltip_columns) > 2:
        raise Exception("You can have at most two columns in a tooltip.")
    tooltip_content = ''
    tooltip_column_names = {} if tooltip_column_names is None else tooltip_column_names
    for col in tooltip_columns:
        assert col in plot_df
        formatting = ''
        if pd.api.types.is_float(plot_df[col].iloc[0]):
            formatting = '.toFixed(6)'
        tooltip_content += '+ "<br />%s: " + d.etc["%s"]%s' % (
            html.escape(tooltip_column_names.get(col, col)),
            col.replace('"', '\\"').replace("'", "\\'"), formatting)
    tooltip_content_js_function = '(function(d) {return d.term %s;})' % tooltip_content
    return tooltip_content_js_function


def get_custom_term_info_js_function(plot_df, term_description_column_names, term_description_columns,
                                     term_word_in_term_description):
    custom_term_html = ''
    term_description_column_names = {} if term_description_column_names is None else term_description_column_names
    for col in term_description_columns:
        assert col in plot_df
        formatting = '.toFixed(6)' if pd.api.types.is_float(plot_df[col].iloc[0]) else ''
        custom_term_html += '+ "<b>%s:</b> " + d.etc["%s"]%s + "<br />"' % (
            html.escape(term_description_column_names.get(col, col)),
            col.replace('"', '\\"').replace("'", "\\'"), formatting)
    if custom_term_html != '':
        custom_term_html += '+'
    custom_term_info_js_function = (
            '(d => "%s: "+d.term+"<div class=topic_preview>"%s"</div>")' %
            (
                term_word_in_term_description,
                custom_term_html
            )
    )
    return custom_term_info_js_function