from settings import Settings
import optimize
import json


def create_result_file():

    with open('templates/partials/result.strategy.tmpl.html', 'r') as f:
        tmpl_partial = f.read()
    with open('templates/result.tmpl.html', 'r') as f:
        tmpl_template = f.read()
    with open('templates/layouts/default.tmpl.html', 'r') as f:
        tmpl_layout= f.read()

    setup_manager = Settings.get('SetupManager')()
    items = setup_manager.load_result_setup_items()
    for session in items:
        items[session] = setup_manager.group_setup_items_by_strategy(items[session])
    rows = ''
    content = ''
    for session in items:
        for strategy_name in items[session]:
            rows = ''
            for item in items[session][strategy_name]:
                partial = tmpl_partial
                partial = partial.replace('{asset}', str(item.symbol))
                partial = partial.replace(
                    '{amount_trades}', str(item.result.amount_trades))
                partial = partial.replace('{wins}', str(item.result.wins))
                partial = partial.replace('{losses}', str(item.result.losses))
                partial = partial.replace('{drawdown}', str(round(item.result.drawdown)))

                p = ''
                for parameter in item.get_parameter_keys():
                    value = str(getattr(item.parameters, parameter))
                    if value:            
                        p += parameter + ': ' + str(getattr(item.parameters, parameter)) + ', '
                partial = partial.replace('{parameters}', p)
                partial = partial.replace(
                    '{result_per_trade}', str(round(item.result.result_per_trade, 2)))
                partial = partial.replace(
                    '{result_pips}', str(round(item.result.result_pips)))
                rows += partial

                result = tmpl_template
                result = result.replace('{strategy_name}', strategy_name)
                result = result.replace('{from}', item.result.start_time)
                result = result.replace('{to}', item.result.end_time)
                result = result.replace('{rows}', rows)
                result = result.replace('{session}', session)
        content += result

    
    content = tmpl_layout.replace('{main}', content)



    with open('public/result.html', 'w') as f:
        f.write(content)


if __name__ == '__main__':
    create_result_file()
