"""
Wrappers for IUCN API calls.

API documentation can be found at: https://apiv3.iucnredlist.org/api/v3/docs
"""
from typing import Union
from urllib.parse import urljoin

import pandas as pd
import requests

from ..utils import expand_result

API_URL = "https://apiv3.iucnredlist.org/api/v3/"


def _request(url: str, token: str) -> requests.Response:
    """
    Creates a request for the IUCN API and handles HTTP exceptions.

    Parameters
    ----------
    url:   IUCN API endpoint.
    token: IUCN API authentication token.

    Returns
    -------
    Request response.
    """
    try:
        response = requests.get(url, params={"token": token})
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise Exception(f"Error calling IUCN API. {err}")
    if "message" in response.json():
        msg = response.json()["message"]
        raise Exception(f"Error calling IUCN API. {msg}")

    return response


def get_country_occurrence(
    names: pd.Series,
    token: str,
    add_supplied_names: bool = False,
    add_source: bool = False,
    expand: bool = True
) -> pd.DataFrame:
    """
    Gets country occurrence and related information for multiple species
    using the IUCN API.

    Parameters
    ----------
    names:              Scientific name(s) to get results for.
    token:              Species+/CITES checklist API authentication token.
    add_supplied_names: Add supplied scientific names column to the
                        resulting DataFrame.
    add_source:         Add source column to the resulting DataFrame.
    expand:             Expand DataFrame rows to match `names` size. If
                        False, the number of rows will correspond to
                        the number of unique names in `names`.

    Returns
    -------
    Country occurrence DataFrame.
    """
    if isinstance(names, (list, str)):
        names = pd.Series(names)

    endpoint = urljoin(API_URL, "species/countries/name/")
    df = pd.DataFrame()

    unique_names = names.dropna().unique()
    for name in unique_names:
        response = _request(urljoin(endpoint, name), token)
        if response.json().get("result"):
            temp_df = pd.DataFrame(response.json()["result"])
            result = pd.Series({
                field: values for field, values in zip(temp_df.columns, temp_df.T.values)
            })
        else:
            result = pd.Series([], dtype="object")
        df = df.append(pd.Series(result), ignore_index=True)

    if add_supplied_names:
        df["supplied_name"] = unique_names
    if add_source:
        df["source"] = "IUCN"
    if expand:
        df = expand_result(names, df)

    return df


def get_species_info(
    names: Union[list, pd.Series, str],
    token: str,
    add_supplied_names: bool = False,
    add_source: bool = False,
    expand: bool = True
) -> pd.DataFrame:
    """
    Gets IUCN category and miscellaneous information for multiple species
    using the IUCN API.

    Parameters
    ----------
    names:              Scientific name(s) to get results for.
    token:              Species+/CITES checklist API authentication token.
    add_supplied_names: Add supplied scientific names column to the
                        resulting DataFrame.
    add_source:         Add source column to the resulting DataFrame.
    expand:             Expand DataFrame rows to match `names` size. If
                        False, the number of rows will correspond to
                        the number of unique names in `names`.

    Returns
    -------
    Species info DataFrame.
    """
    if isinstance(names, (list, str)):
        names = pd.Series(names)

    endpoint = urljoin(API_URL, "species/")
    df = pd.DataFrame()

    unique_names = names.dropna().unique()
    for name in unique_names:
        response = _request(urljoin(endpoint, name), token)
        if response.json().get("result"):
            result = pd.Series(response.json()["result"][0])
        else:
            result = pd.Series([], dtype="object")
        df = df.append(pd.Series(result), ignore_index=True)

    if add_supplied_names:
        df["supplied_name"] = unique_names
    if add_source:
        df["source"] = "IUCN"
    if expand:
        df = expand_result(names, df)

    return df
