import numpy as np

CONFIG = {
    "percentiles" : np.array([0.025,0.05,0.5,0.95,0.975]),
    "ciudades" : ["TRUJILLO","LIMA","AREQUIPA"]
}

rev_fmt = {
    "media": "{:.2f}",
    "desv": "{:.2f}",
    **{f"{perc:.0%}" : "{:.2f}" for perc in CONFIG['percentiles'][100*CONFIG['percentiles']%1 == 0]},
    **{f"{perc:.1%}" : "{:.2f}" for perc in CONFIG['percentiles'][100*CONFIG['percentiles']%1 != 0]},
}

trip_fmt = {
    "media": "{:.2f}",
    "desv": "{:.2f}",
    **{f"{perc:.0%}" : "{:.0f}" for perc in CONFIG['percentiles'][100*CONFIG['percentiles']%1 == 0]},
    **{f"{perc:.1%}" : "{:.0f}" for perc in CONFIG['percentiles'][100*CONFIG['percentiles']%1 != 0]},
}

def validate_num_from_txt(text,dtype=float,ll=1,ul=1000):
    string = ''
    if dtype==int:
        string = ' whole'

    numbers = None
    error = None
    try:
        numbers = np.array([
            dtype(x.strip())
            for x in text.split(",")
        ],dtype=dtype)
    except ValueError:
        error = f"Please enter only{string} numbers separated by commas."
        return None, error
    if numbers is not None:
        if (numbers < ll).any() or (numbers > ul).any():
            error = f"Please enter only{string} numbers from {ll} up to {ul}."
            return None, error

    return numbers, error