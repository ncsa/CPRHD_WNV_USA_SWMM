import glob
from swmmtoolbox import swmmtoolbox
from matplotlib import pyplot as plt
import calendar
import os
from tqdm import tqdm



def compare_all(states):
    extract_vars = [['system', 'Rainfall', 'Rainfall'],['system','Runoff','Runoff'],['system','Evaporation_infiltration','Evaporation_infiltration']]

    date = [i for i in range(365)]
    width = 1.0

    for state in tqdm(states):
        state_name = state[0].upper() + state[1:]

        daily = glob.glob('./daily/simulation_files/' + state + '*.out')
        hourly = glob.glob('./hourly/simulation_files/' + state + '*.out')
        prism = glob.glob('./prism/simulation_files/' + state + '*.out')

        daily_dry = glob.glob('./daily/simulation_files/dry_only_test/' + state + '*.out')
        hourly_dry = glob.glob('./hourly/simulation_files/dry_only_test/' + state + '*.out')
        prism_dry = glob.glob('./prism/simulation_files/dry_only_test/' + state + '*.out')


        if not len(daily) and len(hourly) and len(prism) > 0:
            print('Failed to find one or more files for', state)
            break

        daily_data = swmmtoolbox.extract(daily[0], *extract_vars).resample('d').sum()
        hourly_data = swmmtoolbox.extract(hourly[0], *extract_vars).resample('d').sum()
        prism_data = swmmtoolbox.extract(prism[0], *extract_vars).resample('d').sum()

        daily_dry_data = swmmtoolbox.extract(daily_dry[0], *extract_vars).resample('d').sum()
        hourly_dry_data = swmmtoolbox.extract(hourly_dry[0], *extract_vars).resample('d').sum()
        prism_dry_data = swmmtoolbox.extract(prism_dry[0], *extract_vars).resample('d').sum()

        for data in ['system__Rainfall', 'system__Evaporation_infiltration', 'system__Runoff']:
            data_name = data[8:]
            out_dir = './plots/new_combined_plots/dry_only_comparison/'
            if not os.path.exists(out_dir):
                print('Making', out_dir)
                os.makedirs(out_dir)

            outfile = out_dir + state + '_' + data_name + '.svg'

            fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(20, 16))

            # Original Data
            axes[0,0].set_title('3 Hour NARR')
            axes[0,0].bar(date, hourly_data[data], width, label=data_name)

            axes[0,1].set_title('Daily NARR')
            axes[0,1].bar(date, daily_data[data], width, label=data_name)

            axes[0,2].set_title('Daily PRISM')
            axes[0,2].bar(date, prism_data[data], width, label=data_name)


            # Dry Only Data
            axes[1,0].set_title('3 Hour NARR - Dry Only: NO')
            axes[1,0].bar(date, hourly_dry_data[data], width, label=data_name)

            axes[1,1].set_title('Daily NARR - Dry Only: NO')
            axes[1,1].bar(date, daily_dry_data[data], width, label=data_name)

            axes[1,2].set_title('Daily PRISM - Dry Only: NO')
            axes[1,2].bar(date, prism_dry_data[data], width, label=data_name)


            for row in axes:
                for ax in row:
                    ax.set_xticks([0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334])
                    ax.set_xticklabels(calendar.month_name[1:13], rotation=-90)
                    ax.legend()

            plt.autoscale()
            fig.suptitle(state_name, size=28)
            plt.savefig(outfile, dpi=900)
            plt.show()
            # break
        # break




def compare_dry_plots(states):
    date = [i for i in range(365)]
    width = 1.0
    extract_vars = [['system', 'Rainfall', 'Rainfall'],['system','Runoff','Runoff'],['system','Evaporation_infiltration','Evaporation_infiltration']]


    for state in tqdm(states):
        state_name = state[0].upper() + state[1:]

        out_dir = './plots/dry_only_comparison/' + state + '/'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for sim_type in ['daily', 'hourly', 'prism']:
            if sim_type == 'daily' or 'hourly':
                name = sim_type[0].upper() + sim_type[1:] + ' NARR'
            else:
                name = sim_type.upper()

            dry_only_yes = glob.glob('./' + sim_type + '/simulation_files/' + state + '*.out')[0]
            dry_only_no = glob.glob('./' + sim_type + '/simulation_files/dry_only_test/' + state + '*.out')[0]
            dry_only_yes_data = swmmtoolbox.extract(dry_only_yes, *extract_vars).resample('d').sum()
            dry_only_no_data = swmmtoolbox.extract(dry_only_no, *extract_vars).resample('d').sum()

            for data in ['system__Rainfall', 'system__Evaporation_infiltration', 'system__Runoff']:
                data_name = data[8:]
                outfile = out_dir + state + '_' + sim_type + '_' + data_name + '.svg'

                fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(15,8))

                axes[0].set_title(name + ' - Dry Only: YES')
                axes[0].bar(date, dry_only_yes_data[data], width, label=data_name)

                axes[1].set_title(name + ' - Dry Only: NO')
                axes[1].bar(date, dry_only_no_data[data], width, label=data_name)

                for ax in axes:
                    ax.set_xticks([0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334])
                    ax.set_xticklabels(calendar.month_name[1:13], rotation=-90)
                    ax.legend()

                plt.suptitle(state_name, size=28)
                plt.autoscale()
                plt.savefig(outfile, dpi=900)
                plt.show()


if __name__ == '__main__':
    states = glob.glob('./daily/simulation_files/*.out')
    states = [x[x.rfind('/') + 1:x.rfind('_')] for x in states]
    states = [x[:x.rfind('_')] for x in states]

    compare_dry_plots(states)