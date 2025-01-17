import awkward as ak
import pandas as pd
from .util import get_pivoted, pad_pivoted_l
import pyarrow as pa

waferfields_sums = ['energy', 'simenergy', 'data', 'mipPt', 'pt']
waferfields_firsts = ['waferid', 'subdet', 'zside', 'layer', 
                      'waferu', 'waferv', 'wafertype']
waferfields_means = ['x', 'y', 'z', 'eta', 'phi']
waferfields_simmeans = ['simx', 'simy', 'simz', 'simeta', 'simphi']
waferfields = waferfields_sums + waferfields_firsts \
            + waferfields_means + waferfields_simmeans

def get_waferid(tcs):
    u = tcs['waferu']
    v = tcs['waferv']
    l = tcs['layer']
    z = tcs['zside']
    return z * (l + 60*(u + 20) + 60*40*(v + 20))

def group_by_wafer_l(tcs_l):
    '''
    apply group_by_wafer() to a list of tc arrays
    see group_by_wafer() for docs
    '''
    return [group_by_wafer(tcs) for tcs in tcs_l]

def group_by_wafer(tcs):
    '''
    reshape tc array to group by wafer 
    @param tcs: [awkward recordarray] tcs from get_siwafers()
    @result: [awkward recordarray] the same tcs, grouped by wafer
    '''
    sortvar = get_waferid(tcs)
    sortidx = ak.argsort(sortvar, axis=-1)

    sortvar = sortvar[sortidx]

    tcs = tcs[sortidx]
    runs = ak.flatten(ak.run_lengths(sortvar))
    tcs['waferid'] = sortvar
    tcs = ak.unflatten(tcs, ak.flatten(runs, axis=None), axis=-1)
    return tcs

def make_wafers(tcs):
    '''
    make wafers array from tcs array
    '''
    grouped = group_by_wafer(tcs)
    props = {}
    for var in waferfields_sums:
        props[var] = ak.sum(grouped[var], axis=-1)
    for var in waferfields_firsts:
        props[var] = ak.firsts(grouped[var], axis=-1)
    for var in waferfields_means:
        props[var] = ak.sum(grouped[var] * grouped.energy / props['energy'], axis=-1)
        props['sim'+var] = ak.sum(grouped[var] * grouped.simenergy / props['simenergy'], axis=-1)
    
    return ak.zip(props)

def make_wafers_l(tcs_l):
    '''
    list version of make_wafers()
    '''
    return [make_wafers(tcs) for tcs in tcs_l]

def pivoted_wafer_df_l(wafers_l):
    '''
    convert list of wafer arrays into pandas dataframe
    resulting data frame is row=event, column=wafer
    data frames are padded such that they are the same shape for each chain
        even if there are tcs in some that do not appear in others

    @param: tcs_l [list of awkward recordarrays] list of wafer arrays
                                                 from output of group_by_wafer()
    @result: [pandas dataframe] df with row=event, column=wafer
                                padded to be shape-compatible with eachother 
                                even if the list of wafers in each chain are not identical
    '''

    result = [pivoted_wafer_df(wafers) for wafers in wafers_l]
    return pad_pivoted_l(result)


def pivoted_wafer_df(wafers):
    '''
    Single chain version of pivoted_wafer_df_l()
    Obviously, does not include the same padding
    See pivoted_wafer_df_l() for more docs
    '''
    values = waferfields
    ans = get_pivoted(wafers, values=values, columns='waferid')
    ans.index.name = 'event'
    return ans

def pa_waferdf(waferdf):
    ans = {}
    for field in waferfields:
        if field=='waferid':
            continue
        ans[field] = waferdf[field].to_numpy().flatten()
    return pa.Table.from_pydict(ans)

def pa_waferdf_l(waferdf_l):
    return [pa_waferdf(waferdf) for waferdf in waferdf_l]
