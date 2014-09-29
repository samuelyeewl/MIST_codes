"""

Generates appropriate replacements (masses, BC conditions, and abundances for MESA
inlist files. Outputs lists of replacements that are inputs to make_replacements.py

Args:
    runname: the name of the grid
    Z: the mass fraction in metals
    startype: the mass range of the models

Returns:
    the list of replacements
    
See Also:
    make_replacements: takes the list of replacements as an input
    
Example:
    >>> replist = make_inlist_inputs(runname, Z, startype)

"""

import sys
import numpy as np
import os
import calc_xyz
    
def make_inlist_inputs(runname, Z, startype):
    
    #Array of all masses
    massgrid = lambda i,f,step: np.linspace(i,f,round(((f-i)/step))+1.0)
    bigmassgrid = np.unique(np.hstack((np.array([0.08]), massgrid(0.1,0.3,0.05),\
                                           massgrid(0.3,0.4,0.01), massgrid(0.4,2.0,0.05),\
                                           massgrid(2.0,5.0,0.2), massgrid(5,12,0.5),\
                                           massgrid(12,20,1.0), massgrid(20,40,2), massgrid(40,150,5))
                                        ))
    
    #Choose the correct mass range and boundary conditions                                   
    if (startype == 'VeryLow'):
        massindex = np.where(bigmassgrid <= 0.25)
        bctype = 'tau_100_tables'
        bclabel = ''
    elif (startype == 'LowDiffBC'):
        massindex = np.where((bigmassgrid >= 0.3) & (bigmassgrid < 0.6)) 
        bctype1 = 'tau_100_tables'
        bclabel1 = '_tau100'
        bctype2 = 'photosphere_tables'
        bclabel2 = '_PT'
    elif (startype == 'Intermediate'):
        massindex = np.where((bigmassgrid >= 0.6) & (bigmassgrid < 10.0))
        bctype = 'photosphere_tables'
        bclabel = ''
    elif (startype == 'High'):
        massindex = np.where(bigmassgrid >= 10.0)
        bctype = 'simple_photosphere'
        bclabel = ''
    else:
        print 'Invalid choice.'
        sys.exit(0)

    #Create mass lists
    mapfunc = lambda var: np.str(int(var)) if var == int(var) else np.str(var)
    masslist = map(mapfunc, bigmassgrid[massindex])
        
    #Create BC lists, but LowDiffBC is a special case
    if (startype == 'LowDiffBC'):
        bctablelist = list([bctype1]*np.size(massindex))+list([bctype2]*np.size(massindex))
        bclabellist = list([bclabel1]*np.size(massindex))+list([bclabel2]*np.size(massindex))
    else:
        bctablelist = list([bctype]*np.size(massindex))
        bclabellist = list([bclabel]*np.size(massindex))
    
    #Create abundance lists
    h1h2he3he4z = calc_xyz.calc_xyz(float(Z))
    H1list = [h1h2he3he4z[0]]*np.size(massindex)
    H2list = [h1h2he3he4z[1]]*np.size(massindex)
    He3list = [h1h2he3he4z[2]]*np.size(massindex)
    He4list = [h1h2he3he4z[3]]*np.size(massindex)
    Zlist = [h1h2he3he4z[4]]*np.size(massindex)
        
    #Make list of [replacement string, values]
    replist = [\
            ["<<MASS>>", masslist],\
            ["<<BC_LABEL>>", bclabellist],\
            ["<<BC_TABLE>>", bctablelist],\
            ["<<H1>>", H1list],\
            ["<<H2>>", H2list],\
            ["<<He3>>", He3list],\
            ["<<He4>>", He4list],\
            ["<<Z>>", Zlist],\
        ]
    
    #Special case for LowDiffBC
    if (startype == 'LowDiffBC'):
        replist = [\
                ["<<MASS>>", masslist*2],\
                ["<<BC_LABEL>>", bclabellist],\
                ["<<BC_TABLE>>", bctablelist],\
                ["<<H1>>", H1list*2],\
                ["<<H2>>", H2list*2],\
                ["<<He3>>", He3list*2],\
                ["<<He4>>", He4list*2],\
                ["<<Z>>", Zlist*2],\
            ]

    return replist