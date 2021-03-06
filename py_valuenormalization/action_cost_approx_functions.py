import sys
from math import floor, log, pow

if (sys.version_info > (3, 0)):
    from .action_cost_functions import *
else:
    from action_cost_functions import *

    
###########################################################################################################
################# U S E R   E D I T   C O S T   E S T I M A T I O N   F U N C T I O N S ###################
###########################################################################################################

def approximate_edit_cost(C, alpha, w1, w2, tau, xi, user, show=False, cur_lambda=None, mm=-1, f_alpha=None):
    if show: logmessage(option = 1, cur_lambda = cur_lambda)
    # Calculate the split and merge costs    
    (est_spl_cost, r) = approximate_split_cost(C, alpha, w1, w2, tau, user=user, show=show, f_alpha=f_alpha)
    (est_mrg_cost, est_slamg_cost, est_scamg_cost) = approximate_merge_cost(r, tau, xi, w2, mm, user=user, show=show)
    
    return (est_spl_cost + est_mrg_cost, est_spl_cost, est_mrg_cost, est_slamg_cost, est_scamg_cost, r, 0)


# Calculate splitcost based on the cluster values
def approximate_split_cost(C, alpha, w1, w2, tau, user, show=False, f_alpha=None):
    n = len(C)
    cost = 0.
    r = 0
    for jj in range(n):
        c_j = C[jj]
        psi_j = len(c_j)
        alpha_j = f_alpha(psi_j) if f_alpha is not None else alpha
        beta_j = min(int(floor(-1. * log(psi_j, 1. - alpha_j))), psi_j - 1) if alpha_j != 1. else -1
        if show: logmessage(option = 2, psi_j=psi_j, alpha_j = alpha_j, beta_j = beta_j )
        r += beta_j + 1 if alpha_j != 1. else 1

        cost += rho_f('', user=user, show=False)
        if show: logmessage(option = 3)
        if alpha_j < 0.1:
            cost += rho_s('', user=user, show=False)
            if show: logmessage(option = 4)

        for kk in range(1,beta_j + 1):
            if alpha_j >= 0.1:
                cost += ( 5. * rho_f('', user=user, show=False) ) + ( 4. * rho_s('', user=user, show=False) )
                if show: logmessage(option = 5)
                
                omatjxpi = pow(1. - alpha_j, kk - 1) * psi_j
                pcost1 = rho_p(c_j, inpalpha=alpha_j, clust_size=omatjxpi, user=user, show=False)
                cost += pcost1
                if show: logmessage(option = 6, omatjxpi = omatjxpi, alpha_j = alpha_j, pcost1 = pcost1 )
                
                dcost1 = rho_d(c_j, w1, clust_size=omatjxpi, user=user, show=False)
                cost += dcost1
                if show: logmessage(option = 7, omatjxpi = omatjxpi, dcost1 = dcost1)
                
                cost += (omatjxpi - 1.) * (rho_m('', '', user=user, show=False) + (alpha_j if alpha_j < 0.5 else 1 - alpha_j) * rho_s('', user=user, show=False))
                if show: logmessage(option = 8, omatjxpi = omatjxpi, alpha_j = alpha_j)

            else:
                cost += rho_f('', user=user, show=False) + rho_s('', user=user, show=False)
                cost += psi_j * rho_z('', user=user, show=False)
                cost += int((2 * psi_j * (1. - tau)) + 1) * rho_f('', user=user, show=False)
                cost += int((3 * psi_j * (1. - tau)) + 1) * rho_s('', user=user, show=False)
                if show: logmessage(option = 9, psi_j = psi_j, tau = tau)
                
                cost += w2 * rho_z(c_j, user=user, show=False)
                if show: logmessage(option = 10, w2 = w2)
                
                sch = pow(1. - alpha_j, (kk - 1)*w2) * (tau * psi_j)
                cost += (sch - w2) * rho_r(c_j, user=user, show=False)
                if show: logmessage(option = 11, w2 = w2, sch = sch)
                
                srvch = 0.
                for pp in range(1, w2 + 1):
                    srvch += alpha_j * pow(1. - alpha_j, ((kk - 1)*w2)+pp) * (tau * psi_j) + 1
                cost += int(srvch) * (rho_f('', user=user, show=False) + rho_s('', user=user, show=False))
                if show: logmessage(option = 12, srvch = srvch)

    return (cost, r)


# Calculate mergecost based on the cluster values
def approximate_merge_cost(r, tau, xi, w2, mm, user, show=False, prefix="[[[ APPROX MERGE ]]] "):
    cost = 0.

    cost += r * rho_z('', user=user, show=False)
    cost += int((2 * r * (1. - tau)) + 1) * rho_f('', user=user, show=False)
    cost += int((3 * r * (1. - tau)) + 1) * rho_s('', user=user, show=False)
    if show: logmessage(option = 13, prefix = prefix, r = r, tau = tau)
    est_slamg_cost = cost

    passcnt = int(floor(1. / ( xi * w2 )))
    zcnst, rcnst, fscnst = 0., 0., 0.
    nn = tau * r # mm
    for jj in range(1, passcnt + 1):
        zcnst += w2
        rcnst += ( nn - ( jj * w2 * xi * nn ) - w2 )
        fscnst += ( xi * w2 * nn + 1 )
    cost += int(zcnst) * rho_z('', user=user, show=False)
    cost += int(rcnst) * rho_r('', user=user, show=False)
    cost += int(fscnst) * (rho_f('', user=user, show=False) + rho_s('', user=user, show=False))
    
    if show: logmessage(option = 14, prefix = prefix, zcnst = zcnst, rcnst = rcnst, fscnst = fscnst) 
    est_scamg_cost = cost - est_slamg_cost
    return (cost, est_slamg_cost, est_scamg_cost)




# Log messages while calculating costs if show = true
def logmessage(option=None, cur_lambda=None, psi_j=None, alpha_j=None, beta_j=None, omatjxpi=None, pcost1=None, dcost1=None, tau=None, w2=None, sch=None, srvch=None, prefix=None, r=None, zcnst=None, rcnst=None, fscnst=None ):
      
    if option == 1:
        print("<<<< A P P R O X >>>>")
        print("<<<<<%s>>>>>"%("lambda = %d"%(cur_lambda,) if cur_lambda is not None else "<<<<<>>>>>>", ))
    
    # Log messages for split cost
    if option == 2:
        print("[[[ APPROX SPLIT ]]] psi_j = %d, alpha_j = %.02f, beta_j = %d"%(psi_j, alpha_j, beta_j))
    
    if option == 3:
        print("[[[ APPROX SPLIT ]]] focus")
    
    if option == 4:
        print("[[[ APPROX SPLIT ]]] select")
        
    if option == 5:
        print("[[[ APPROX SPLIT ]]] 3 * focus + 2 * select")
    
    if option == 6:
        print("[[[ APPROX SPLIT ]]] isPure(%d, %.02f)\t[cost = %.02f]"%(omatjxpi, alpha_j, pcost1))
    
    if option == 7:
        print("[[[ APPROX SPLIT ]]] finddom(%d)\t[cost = %.02f]"%(omatjxpi, dcost1))
        
    if option == 8:
        print("[[[ APPROX SPLIT ]]] %d * (match + %.02f * select)"%(omatjxpi - 1., (alpha_j if alpha_j < 0.5 else 1 - alpha_j)))
    
    if option == 9:
        print("[[[ APPROX SPLIT ]]]  %d * recallAndMemorize + %d * focus + %d * select"%(psi_j, int((2 * psi_j * (1. - tau)) + 1), int((3 * psi_j * (1. - tau)) + 1)))
    
    if option == 10:
        print("[[[ APPROX SPLIT ]]] %d * recallAndMemorize"%(w2, ))
        
    if option == 11:
        print("[[[ APPROX SPLIT ]]] %d * recall"%(sch - w2, ))
    
    if option == 12:
        print("[[[ APPROX SPLIT ]]] %d * (focus + select)"%(int(srvch), ))
    
    
    # Log messages for merge cost
    if option == 13:
        print("%s {{SlideAndMerge}} %d * recallAndMemorize + %d * focus + %d * select"%(prefix, r, int((2 * r * (1. - tau)) + 1), int((3 * r * (1. - tau)) + 1)))
    
    if option == 14:
        print("%s {{GlobalMerge}} %d * recallAndMemorize + %d * recall + %d * (focus + select)"%(prefix, int(zcnst), int(rcnst), int(fscnst)))


