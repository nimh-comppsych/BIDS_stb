import click
import sys
import json
import os


@click.command()
@click.argument('json_orig_path', type=click.Path(exists=True)) #help='Path of the original BIDS-format JSON.')
@click.option('--condition_names','-c',multiple=True, help='Condition names as they appear in the BIDS file. Takes multipe inputs separated by -c.')
@click.option('--num_trials', '-n',  default=1, help='Number of trials. Defaults to 1')
@click.option('--json_new_dir','-d', default='.', help='Output directory for new JSONs. Defaults to current working directory.')
def stb_model(json_orig_path, condition_names, num_trials, json_new_dir):
	_stb(json_orig_path, condition_names, num_trials, json_new_dir)


def _stb(json_orig_path, condition_names, num_trials, json_new_dir):
    """Converts BIDS formatted jsons into jsons with single trial beta outputs.
    Takes original json path, target conditions, the number of total trials, and an optional output directory.
    Generates json for each trial of each condition with single trial beta output."""
    for condition_name in condition_names:
        for trial_n in range(num_trials):
            with open(json_orig_path, 'r') as h:
                jdat = json.load(h)

            #Replaces target condition with target trial and other trials regressors
            jdat["Steps"][0]['Model']['X'].remove(condition_name)
            jdat["Steps"][0]['Model']['X'] = [f"trial-{trial_n:03d}_{condition_name}",f"other_trials_{condition_name}"] + jdat["Steps"][0]['Model']['X']

            
            #Removes all model levels other than 1st level, contrasts, and existing dummy contrasts
            jdat['Steps'] = [jdat['Steps'][0]]
            jdat['Steps'][0].pop('Contrasts', None)
            jdat['Steps'][0].pop('DummyContrasts', None)

            #Adds target trial regressors to convolve list
            to_convolve = [x for x in jdat["Steps"][0]['Transformations'] if x["Name"] == "Convolve"][0]["Input"]
            to_convolve.remove(condition_name)
            to_convolve = [f"trial-{trial_n:03d}_{condition_name}",f"other_trials_{condition_name}"] + to_convolve
            [x for x in jdat["Steps"][0]['Transformations'] if x["Name"] == "Convolve"][0]["Input"] = to_convolve

            #Adds target trial regressor to dummy contrast
            jdat["Steps"][0]['DummyContrasts'] = {
                "Conditions": [f"trial-{trial_n:03d}_{condition_name}"],
                "Type":"t"
            }
            #generates output json'''
            json_new_path = os.path.join(json_new_dir, f'stb_trial-{trial_n:03d}_{condition_name}.json')
            with open(json_new_path, 'w') as h:
                json.dump(jdat, h, indent=2)

