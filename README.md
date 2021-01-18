# Telco Churn (zig)
> Churn model + model interpration


## Install

### windows
To create a conda env based on the included conda file

`conda env create --name <env name> -f conda-env.yml`

### linux
`pip install -r requirements.txt`

in a virtuelenv


## Notebooks & visual
Also, order notebooks (raw exploration > features > model > visuals)

1. **00_exploration** - Notebooks used for exploration on the raw data
2. **01_features** - Notebook for generating features on the respective raw data
3. **02A_user_profile** - Combining user profile data + modeling
4. **02B_geolocation_profile** - Combining geo profile data
5. **03A_user_profile_model** - Model for churn prediction
6. **Geo_profile_map** (PowerBI) - Visualizing geo profile data


