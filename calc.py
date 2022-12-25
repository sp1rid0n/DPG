import dearpygui.dearpygui as dpg
import numexpr as ne
import re


def click_callback(sender):
    lbl = dpg.get_item_label(sender)
    expression = dpg.get_value(entry)

    if lbl == "C":
        dpg.set_value(entry, '')

    elif lbl == "=":
        try:
            expression = re.sub('\^', '**', expression)
            evaluated = ne.evaluate(expression)
            if evaluated.dtype == 'float':
                evaluated = round(float(evaluated), 10)

            dpg.set_value(entry, evaluated)

        except SyntaxError:
            dpg.set_value(entry, "Syntax error! Clear to continue!")

        except ZeroDivisionError:
            dpg.set_value(entry, "Zero division error! Clear to continue!")

    else:
        dpg.set_value(entry, expression+lbl)


dpg.create_context()
dpg.create_viewport(title='DearPyGUI Calculator', width=300, height=300)

SIZE_ITEM = 75
WIDTH = 300
HEIGHT = 300
PADDING = 4

with dpg.window(tag='DPG', label='Calculator', no_resize=True, no_close=True, width=WIDTH, height=HEIGHT):
    entry = dpg.add_input_text(tag='Entry')
    dpg.set_item_width(entry, WIDTH-40)
    labels = ['123+', '456-', '789*', '.0^/', 'C=']
    for row in labels:
        with dpg.group(horizontal=True):
            for item in row:
                btn = dpg.add_button(label=item, tag=f'Btn_{item}')
                dpg.set_item_callback(btn, click_callback)
                dpg.set_item_user_data(btn, entry)
                dpg.set_item_height(btn, 40)
                dpg.set_item_width(btn, WIDTH // len(row) - (32 - PADDING * len(row)))

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window('Primary Window', True)
dpg.start_dearpygui()
dpg.destroy_context()
