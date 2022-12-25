import dearpygui.dearpygui as dpg
import math
import numpy as np
import time
import re
import numexpr as ne


start_angle = 18
tick_angle = 4.5
cnt_ticks = 32

last_time = time.time()
period = 1
rand_volatage = 12

ORANGE = [255, 107, 43]
WHITE = [227, 227, 227]
BLACK = [48, 48, 48]

voltages = []
mean_voltages = []
volt_transition = []


def period_change(node):
    global period
    period = int(dpg.get_value(node))
    dpg.set_item_label('series_tag', f"Mean voltage {period} sec.")
    global mean_voltages
    mean_voltages = []

    dpg.delete_item('volt_avg_text')
    draw_avg_volt(0.0, [-90, 10])


def voltage_change(node):
    global rand_volatage
    rand_volatage = int(dpg.get_value(node))
    global mean_voltages
    mean_voltages = []


def draw_volt(val, pos):
    string = f"{round(val, 1)}V"
    dpg.draw_text(pos, string, size=20, color=WHITE,
                  parent='volt_text_node', tag='volt_text')


def draw_avg_volt(val, pos):
    string = f"{round(val, 1)}V"
    dpg.draw_text(pos, string, size=20, color=WHITE,
                  parent='volt_text_node', tag='volt_avg_text')


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


def draw_analog():
    cur_angle = start_angle
    with dpg.drawlist(tag='analog_meter', width=400, height=250):
        with dpg.draw_node(tag="root_node"):
            for i in range(cnt_ticks + 1):
                with dpg.draw_node():
                    if i % 2 == 0:
                        dpg.draw_line([130, 0], [150, 0],
                                      thickness=2, color=BLACK)
                        num = cnt_ticks // 2 - i // 2
                        if num % 2 == 0:
                            str_num = str(num)
                            if len(str_num) > 1:
                                dpg.draw_text(
                                    [125 - len(str_num) * 6, 3 - len(str_num) * 5], str_num, size=14, color=BLACK)
                            else:
                                dpg.draw_text(
                                    [125 - len(str_num) * 5, 0], str_num, size=14, color=BLACK)
                    else:
                        dpg.draw_line([135, 0], [150, 0],
                                      thickness=1, color=BLACK)

                    dpg.apply_transform(
                        dpg.last_container(),
                        dpg.create_rotation_matrix(math.pi * cur_angle/180.0, [0, 0, -1]))
                    cur_angle += tick_angle

            with dpg.draw_node(tag="hand_node", user_data=[time.time(), 0]):
                dpg.draw_line([0, 0], [150, 0], thickness=4, color=ORANGE)
                dpg.draw_circle([0, 0], 8, fill=ORANGE)

            with dpg.draw_node(tag='volt_text_node'):
                pos_cur = [[30, 10], [90, 30]]
                pos_avg = [[-90, 10], [-30, 30]]
                dpg.draw_text([30, -10], 'current', size=14, color=BLACK, parent='volt_text_node')
                dpg.draw_rectangle(
                    pos_cur[0], pos_cur[1], color=BLACK, fill=BLACK)
                draw_volt(0, pos_cur[0])

                dpg.draw_text([-90, -10], 'mean', size=14,
                              color=BLACK, parent='volt_text_node')
                dpg.draw_rectangle(
                    pos_avg[0], pos_avg[1], color=BLACK, fill=BLACK)
                draw_avg_volt(0, pos_avg[0])

    dpg.apply_transform("root_node", dpg.create_translation_matrix([200, 200]))


def hand_ratation(voltages, volt_transition):
    last_time, last_rot = dpg.get_item_user_data("hand_node")

    if len(volt_transition) > 0:
        hand_rot = volt_transition.pop(0)
        dpg.apply_transform("hand_node", dpg.create_rotation_matrix(
            math.pi * hand_rot / 180.0, [0, 0, -1]))
    if time.time() - last_time >= 0.1:
        voltage = np.random.normal(rand_volatage, 0.6)
        voltages.append(voltage)
        hand_rot = cnt_ticks * tick_angle + start_angle - voltage * 9

        volt_transition.extend(
            list(np.interp([i for i in range(0, 5)], [0, 5], [last_rot, hand_rot])))

        last_time = time.time()
        last_rot = hand_rot

        dpg.delete_item('volt_text')
        draw_volt(voltage, [30, 10])

    dpg.set_item_user_data("hand_node", [last_time, last_rot])


def avg_volt_update(mean_voltages, voltages, span):
    last_time = dpg.get_item_user_data("series_tag")
    if time.time() - last_time >= period:
        mean_voltages.append(np.mean(voltages))
        last_time = time.time()
        voltages.clear()

        dpg.delete_item('volt_avg_text')
        draw_avg_volt(np.mean(mean_voltages), [-90, 10])

    dpg.set_item_user_data("series_tag", last_time)

    while len(mean_voltages) > 20:
        mean_voltages.pop(0)

    x = [i for i in range(0, min(span, len(mean_voltages)))]
    dpg.set_value(
        'series_tag', [x, mean_voltages[max(-span, -len(mean_voltages)):]])


dpg.create_context()
dpg.create_viewport(title='DPG', width=720, height=700, resizable=False)

with dpg.window(
    label="Voltmeter", width=420, height=700, pos=(0, 0), tag="window",
    no_resize=True, no_move=True, no_close=True, no_collapse=True
):
    draw_analog()
    with dpg.group(tag='voltmeter_group'):

        dpg.add_text('SEC.')
        sl1 = dpg.add_slider_int(
            default_value=period, width=250, min_value=1, max_value=60, callback=period_change)
        dpg.add_text('Volt.')
        sl2 = dpg.add_slider_int(
            default_value=12, width=250, min_value=3, max_value=14, callback=voltage_change)

    with dpg.plot(label="plot", height=290, width=400):
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="", tag="x_axis")
        dpg.add_plot_axis(dpg.mvYAxis, label="Voltage", tag="y_axis")

        dpg.add_line_series(
            [], [], label=f"Mean voltage {period} sec.", parent="y_axis", tag="series_tag", user_data=0)
        dpg.set_axis_limits('y_axis', 0, 16)
        dpg.set_axis_limits('x_axis', 0, 20)


with dpg.item_handler_registry(tag="hand_rotation_anim"):
    dpg.add_item_visible_handler(
        callback=lambda _: hand_ratation(voltages, volt_transition))
    dpg.add_item_visible_handler(
        callback=lambda _: avg_volt_update(mean_voltages, voltages, 20))
dpg.bind_item_handler_registry("analog_meter", "hand_rotation_anim")


with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, WHITE,
                            category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, BLACK,
                            category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, WHITE,
                            category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, WHITE,
                            category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab,
                            ORANGE, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding,
                            5, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvPlotCol_Line, ORANGE,
                            category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_LegendBg, WHITE,
                            category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_PlotBorder, BLACK,
                            category=dpg.mvThemeCat_Plots)
        dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight,
                            2, category=dpg.mvThemeCat_Plots)

with dpg.theme() as item_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, WHITE,
                            category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered,
                            WHITE, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive,
                            WHITE, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab,
                            ORANGE, category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive,
                            ORANGE, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding,
                            3, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize,
                            1, category=dpg.mvThemeCat_Core)


SIZE_ITEM = 75
WIDTH = 300
HEIGHT = 700
PADDING = 4

with dpg.window(label='Calculator', pos=(420, 0), tag="calc",
                no_resize=True, no_move=True, no_close=True, no_collapse=True, width=WIDTH, height=HEIGHT):
    entry = dpg.add_input_text(tag='Entry')
    dpg.set_item_width(entry, WIDTH-40)
    labels = ['123+', '456-', '789*', '.0^/', 'C=']
    for row in labels:
        with dpg.group(horizontal=True):
            for item in row:
                btn = dpg.add_button(label=item, tag=f'Btn_{item}')
                dpg.bind_item_theme(btn, item_theme)
                dpg.set_item_callback(btn, click_callback)
                dpg.set_item_user_data(btn, entry)
                dpg.set_item_height(btn, 40)
                dpg.set_item_width(btn, WIDTH // len(row) -
                                   (32 - PADDING * len(row)))


dpg.bind_theme(global_theme)
dpg.bind_item_theme(sl1, item_theme)
dpg.bind_item_theme(sl2, item_theme)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
