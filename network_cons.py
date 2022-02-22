import numpy as np

def init( step_num, mode_num, proportion, h, late_comer_mode, t_emerge ):
    degrees = np.zeros( step_num, dtype = 'int' )

    #init state
    degrees[:2] = 1 #a dyad
    modes = np.random.choice(mode_num, size = step_num, p = [proportion,  1 - proportion])
    
    late_entrance( modes, late_comer_mode, t_emerge )

    homophily_mat = symmetric_homophily_construct( h, step_num, mode_num, modes )
    
    return degrees, modes, homophily_mat

def fitness_init( step_num, distribution ):
    if distribution == 'identical':
        return np.ones( step_num )
    elif distribution == 'uniform':
        return np.random.uniform( size = step_num )

def late_entrance( modes, late_comer_mode, t_emerge ): #currently for only two modes
    
    modes[ :t_emerge ] = 1 - late_comer_mode #currently for only two modes
    #modes[ len(modes) - t_emerge: ] = late_comer_mode
    #currently only replaces the late_comers in the begining, with the other group


def symmetric_homophily_construct( h, step_num, mode_num, modes ):
    homophily_mat = np.zeros( ( mode_num , step_num) )
    for mode in range( mode_num ):
        homophily_mat[mode, modes == mode] = h
        homophily_mat[mode, modes != mode] = 1-h
    return homophily_mat

def net_grow( step_num, mode_num, proportion, h, k_init, late_comer_mode\
 , t_emerge, t_unbias, distribution, history_step_size, eps):

    degrees, modes, homophily_mat = init( step_num, mode_num, proportion, h, late_comer_mode, t_emerge )
    
    fitnesses = fitness_init( step_num, distribution )
    
    importances = degrees.astype( 'float' )
    attachment_probabilities = degrees.astype( 'float' )
    
    
    if history_step_size:
        history_steps = np.arange( history_step_size, step_num, history_step_size )
        degrees_history = np.zeros( shape = [ len( history_steps )  ] + list( degrees.shape ) )
    
    #value = 1
    #eps_inv = 1 / eps
#     print(importances)
    for step in range(2, step_num):
        
#         print( 'step: ', step )

#         print( degrees[ degrees > 0 ] )
        
        degrees[step] += k_init #newcomer getting edges
        importances[step] += k_init #* value

        mode = modes[step]

        #old nodes getting edges
        #attachment_probabilities = ( degrees[:step] * homophily_mat[mode, :step] )
        #attachment_probabilities /= attachment_probabilities.sum()
        last_attachment_probabilities = np.copy( attachment_probabilities )
        attachment_probabilities = ( importances[:step] * homophily_mat[mode, :step] * fitnesses[:step] )
        if not attachment_probabilities[:step].sum():
            return last_attachment_probabilities, attachment_probabilities

        
        
        attachment_probabilities[:step] /= attachment_probabilities[:step].sum()
        
        

        old_attached = np.random.choice(step, size = k_init, p = attachment_probabilities) # may output repeated index
        
        for old_index in old_attached:
            degrees[old_index] += 1
            importances[old_index] += 1
        
#         importances[:step] /= importances[:step].sum()
        importances[:step] *= eps

        
        #value *= eps_inv

        #if (step % 5000) == 0:
            #print(step)
        #print( degrees[ degrees > 0 ] )

        if history_step_size:
            if (step % history_step_size) == 0:
                degrees_history[ step // history_step_size - 1 ] = degrees


        if step == t_unbias:
            #print(step)
            homophily_mat = symmetric_homophily_construct( 0.5, step_num, mode_num, modes )
        #print( old_attached )
        #print( importances )
        #print(eps)
        #print( degrees[ degrees > 0 ] )
#         print( attachment_probabilities )
        
    if history_step_size:
        return degrees_history, history_steps, degrees, modes, fitnesses
    else:
        return degrees, modes, fitnesses