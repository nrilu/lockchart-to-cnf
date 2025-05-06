#!/usr/bin/python3
import itertools
import subprocess
import random
import time
import matplotlib.pyplot as plt
import numpy as np
import argparse


show_lockchart=True   # show a pyplot rendering of the lockchart
solve=True            # also solve the cnf
solver="kissat"       # select the solver

#Options for fancy print of solution verification
show_only_one_lock = True     #limit clutter
show_lock_idx = 5             #which lock to show
max_fancy_blocked_keys = 5    #how many keys to show for that lock
max_fancy_keys_and_locks = 10 #how many individual keys & locks to show


#Constants
J = 1  # max jump of depth
MK= 3  # no. of master keys
keys_per_lock_random = 2  #how many keys for each lock, when doing random lock-chart

parser = argparse.ArgumentParser(description="Lock-Chart to CNF Generator")
parser.add_argument('-l', '--locks', type=int, default=50, help='Number of locks (default: 50)')
parser.add_argument('-r', '--random_density', type=float, default=0.0,
                    help='Random key-to-lock probability in range [0,1] (default: 0 = fixed structured)')
parser.add_argument('-p', '--positions', type=int, default=8, help='Number of positions (default: 8)')
parser.add_argument('-d', '--depths', type=int, default=4, help='Number of depths (default: 4)')
args = parser.parse_args()

L = args.locks
random_density = args.random_density
P = args.positions
D = args.depths


if random_density > 0:
    print("Randomized lockchart", random_density)
else:
    print("Fixed sparse lockchart")


R = range #python shorthand
keys_of_lock = [[] for l in R(L)]
blocked_keys_of_lock = [[] for l in R(L)]

def add_keys_to_locks():
    if random_density>0:
        n_keys = L * keys_per_lock_random
        for k in range(n_keys):
            for l in R(L):
                if random.random() < random_density:
                    keys_of_lock[l].append(k)
        return n_keys

    else:
        #General key: opens every lock
        k = 0 #key number
        for l in R(L):
            keys_of_lock[l].append(k)

        #Master key: opens a section of locks
        k+=1
        locks_per_general_key = int(L / MK)
        if L % MK != 0: locks_per_general_key += 1
        for locksection in chunks(R(L),locks_per_general_key):
            for l in locksection:
                keys_of_lock[l].append(k)
            k+=1

        #Ascending key: Opens increasingly large sections of locks
        to_cover=2
        covered=0
        l = 0
        while l<L:
            keys_of_lock[l].append(k)
            covered+=1
            l+=1
            if covered==to_cover and l<L:
                covered=0
                to_cover+=1
                k+=1
        k+=1

        #Triple key: Opens three locks
        for locktriple in chunks(R(L),3):
            for l in locktriple:
                keys_of_lock[l].append(k)
            k+=1

        #Single key: Opens a single lock
        for l in R(L):
            keys_of_lock[l].append(k)
            k+=1

        return k # the total number of created keys

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def extract_blocked_keys_per_lock():
    for l in R(L):
        for k in R(K):
            if k not in keys_of_lock[l]:
                blocked_keys_of_lock[l].append(k)


def print_lockchart():
    print("Keys per lock")
    for l,keys in enumerate(keys_of_lock):
        print("Lock",l,":",keys)


def plot_lockchart():
    lock_key_matrix = np.zeros((L, K), dtype=int)

    # Populate the matrix: 1 (black) if key is part of the lock
    for lock_index, keys in enumerate(keys_of_lock):
        for key in keys:
            if 0 <= key < K:
                lock_key_matrix[lock_index, key] = 1

    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif"
    })

    fig, ax = plt.subplots(figsize=(5, 4))

    ax.set_xlim(-0.5, K - 0.5)
    ax.set_ylim(L - 0.5, -0.5)

    # Add black rectangles for filled cells
    for i in range(L):
        for j in range(K):
            if lock_key_matrix[i, j] == 1:
                rect = plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                     facecolor='black', edgecolor='white',
                                     linewidth=0.5)
                ax.add_patch(rect)

    lock_ticks = np.arange(0, L, 1)
    ax.set_yticks(lock_ticks)

    key_ticks = np.arange(0, K, 1)
    ax.set_xticks(key_ticks)
    ax.tick_params(axis='both', which='major', length=0, width=0)  #
    ax.xaxis.set_ticks_position('top')
    ax.xaxis.set_label_position('top')

    #Grid lines to visually separate cells
    ax.set_xticks(np.arange(K) - 0.5, minor=True)
    ax.set_yticks(np.arange(L) - 0.5, minor=True)
    ax.grid(which="minor", color="black", linestyle='-', linewidth=0.5)
    ax.tick_params(which="minor", size=0)


    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(which="minor", color="lightgray", linestyle='-', linewidth=0.5)
    plt.xlabel("Keys",fontsize=16)
    plt.ylabel("Locks",fontsize=16)

    plt.tight_layout()
    # plt.savefig("pdf-lockchart.pdf", format="pdf", dpi=300,
    #             bbox_inches='tight', transparent=False, backend='pdf')
    plt.show()

def key(k,p,d):
    return 0 + k*PD + p*D + d + 1

def lock(l,p,d):
    return KPD + l*PD + p*D + d + 1

def block(l,k,p,d):
    return KPD + LPD + l*KPD + k*PD + p*D + d + 1

def add_OR_equivalence(A, x):
    #Encodes A <==> x, with A = (a_1 OR a_2 OR ... OR a_n)

    #Step A ==> x: If any a is true, x must be true
    for a in A:
        clauses.append([-a, x])

    #Step x ==> A: If x is true, at least one a must be true
    c = [-x] + A
    clauses.append(c)


def add_AND_equivalence(A, x):
    #Encodes  A <==> x, with A = (a1 AND a2 AND ... AND an)

    #Step A ==> x: if all a are true, x must be true
    c = [-a for a in A] + [x]
    clauses.append(c)

    #Step x ==> A: if x is true, each a must be true
    for a in A:
        clauses.append([-x, a])

def enforce_keys_have_a_depth():
    #Each key must have for each position p at least one cutting depth d
    for k in R(K):
        for p in R(P):
            c = [key(k,p,d) for d in R(D)]
            clauses.append(c)

def enforce_keys_have_at_most_one_depth():
    #Each key can have for each position p at most one cutting depth d
    for k in R(K):
        for p in R(P):
            for (d1,d2) in itertools.combinations(R(D), 2):
                c = [-key(k,p,d1),-key(k,p,d2)] #Pairwise binary prohibit
                clauses.append(c)

def enforce_openings_strict():
    # If key k can open lock l, all it's cuts (p,d) must be allowed by the lock
    # Strict encoding uses an equivalence instead of only an implication,
    # thus for every pin that is introced (every lock-variable set to true), there must also be a corresponding key-tooth that requires this pin
    for l in R(L):
        for p, d in itertools.product(R(P), R(D)):
            key_tooths = []
            for k in keys_of_lock[l]:
                key_tooths.append(key(k,p,d))
            add_OR_equivalence(key_tooths, lock(l, p, d))

def enforce_openings_lazy():
    # If key k can open lock l, all it's tooths (p,d) must be allowed by the lock
    # Lazy encoding allows for pins in locks that are not matched to any key,
    # which is undesirable as each extra cutting increases manufacturing costs and decreases lock security.
    # However, once a solution is found, superfluous pins in locks can be remover in linear time by checking all keys that open given lock for their cutting depths.
    for l in R(L):
        for k in keys_of_lock[l]:
            for p, d in itertools.product(R(P), R(D)):
                c  = [-key(k,p,d), lock(l,p,d)]
                clauses.append(c)

def enforce_blocks_strict():
    #If key k is blocked by lock l, then there must be at least one tooth of the key that does not match lock pin
    for l in R(L):
        #define a block
        for k in blocked_keys_of_lock[l]:
            for p, d in itertools.product(R(P), R(D)):
                key_and_lock_differ = [key(k,p,d),-lock(l,p,d)]
                add_AND_equivalence(key_and_lock_differ, block(l, k, p, d))
        #enforce at least one block per key
        for k in blocked_keys_of_lock[l]:
            c = []
            for p, d in itertools.product(R(P), R(D)):
                c.append(block(l,k,p,d))
            clauses.append(c)

def enforce_blocks_lazy():
    # If key k is blocked by lock l, then there must be at least one tooth of the key that does not have any matching lock pin
    # Enforce at least one block per prohibited key-lock pair
    for l in R(L):
        for k in blocked_keys_of_lock[l]:
            c = []
            for p, d in itertools.product(R(P), R(D)):
                c.append(block(l, k, p, d))
            clauses.append(c)
    # A block enforces that key and lock don't match at that cut
    # block(l,k,p,d) ==> key(k,p,d) AND -lock(l,p,d)
    for l in R(L):
        for k in blocked_keys_of_lock[l]:
            for p, d in itertools.product(R(P), R(D)):
                clauses.append([-block(l,k,p,d), key(k,p,d)])
                clauses.append([-block(l,k,p,d), -lock(l,p,d)])


def enforce_jumps():
    #The difference in neighbouring cutting depths can be at most J
    for k in R(K):
        for p in R(P-1):
            for (d, d_next) in itertools.product(R(D),R(D)):
                if abs(d-d_next)>J:
                    clauses.append([-key(k,p,d),-key(k,p+1,d_next)])



def write_cnf(path):
    with open(path, 'w') as file:
        file.write("p cnf " + str(N_VARS) + " " + str(len(clauses)) + "\n")
        for c in clauses:
            file.write(" ".join(map(str, c)) + " 0\n")


K = add_keys_to_locks()
PD = P*D
KPD = K * PD
LPD = L * PD
N_VARS = KPD + LPD + K*L*PD

extract_blocked_keys_per_lock()
print_lockchart()

clauses = []
enforce_keys_have_a_depth()
enforce_keys_have_at_most_one_depth()
#Test between strict/lazy encoding for both openings and blocks (either implication or equivalence)
encoding_choice = "sl"  #ss,sl,ls,ll
enforce_openings_lazy() if encoding_choice[0]=="l" else enforce_openings_strict()
enforce_blocks_lazy()   if encoding_choice[1]=="l" else enforce_blocks_strict()
enforce_jumps()


tag = time.time()
instance_name = f"results/lockchart-L{L}-K{K}-p{P}d{D}j{J}-t{tag}"
if random_density>0:
    instance_name = f"results/lockchart-L{L}-rnd{random_density}-K{K}-P{P}D{D}J{J}-t{tag}"

cnf_path = instance_name + ".cnf"
write_cnf(cnf_path)

if show_lockchart:
    plot_lockchart()



# End of cnf generation

# --------------------------------------------------------------------------------------------------------------#

# Start of optional solving & interpreting


def solve_lockchart():
    process = subprocess.Popen(
        solver + " " + cnf_path,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1  # line-buffered for live read
    )

    output_lines = []
    for line in process.stdout:
        print(line, end='')
        output_lines.append(line)

    process.stdout.close()
    process.wait()
    output_lines = ''.join(output_lines)

    for line in output_lines.splitlines():
        if line == "s UNSATISFIABLE":
            return "UNSAT", output_lines, []

    model = [0 for i in range(N_VARS+1)]
    for line in output_lines.splitlines():
        if line[0] == "v":
            literals = line[2:].split(" ")
            literals = [int(l) for l in literals]
            for l in literals:
                model[abs(l)]= (l>0)

    return "SAT", output_lines, model


def extract_key_cuts(model):
    keys = []
    for k in R(K):
        cuts = []
        for p in R(P):
            for d in R(D):
                if model[key(k,p,d)]:
                    cuts.append(d)
        keys.append(cuts)
    return keys

def extract_lock_pins(model):
    locks = []
    for l in R(L):
        pins = []
        for p in R(P):
            pins_per_pos = []
            for d in R(D):
                if model[lock(l,p,d)]:
                    pins_per_pos.append(d)
            pins.append(pins_per_pos)
        locks.append(pins)
    return locks


def fancy_lock_print(lock_pins):
    for l,lock in enumerate(lock_pins):
        if l > max_fancy_keys_and_locks:
            continue
        print("Lock",l,"-----------------------------")
        lines = ["             "] * D
        for d in range(D):
            for pins_per_pos in lock:
                lines[d] += str(d) if d in pins_per_pos else "."
            lines[d] += "  "
        for line in lines:
            print(line)
        print()

def fancy_key_print(all_key_cuts):
    for k,cuts in enumerate(all_key_cuts):
        if k > max_fancy_keys_and_locks:
            continue
        print(f"Key {k}: {str(cuts)}")
        lines    = ["         "] * D
        for cut in cuts:
            for d in range(D):
                lines[d] += str(cut) if d==cut else "."
        for line in lines:
            print(line)
        print("")


def verify_jumps(all_key_cuts):
    print("\n \n \nVerify jumps")
    for k,cuts in enumerate(all_key_cuts):
        for i in range(len(cuts)-1):
            if abs(cuts[i]-cuts[i+1])>J:
                print("key",k,"cuts",cuts)
                print("error, key cuts jump too much")
                return False
    print("All key profiles verified, all respect max jump.")
    return True


def verify_open(all_lock_pins, all_key_cuts):
    print("\n \n \nSample of opening keys-lock combos")
    for l in R(L):
        show = (l == show_lock_idx or not show_only_one_lock)
        lock_pins = all_lock_pins[l]
        for k in keys_of_lock[l]:
            if show: print("  Key",k," into Lock",l,"------------------------------")
            key_cuts = all_key_cuts[k]
            for d,pins in zip(key_cuts,lock_pins):
                if show: print(f"    {d} {pins}".ljust(20) + "...")
                if d not in pins:
                    print("error, key doesnt open lock")
                    return False
    return True


def verify_block(all_lock_pins, all_key_cuts):
    print("\n \n \nSample of blocked key-lock combos")
    for l in R(L):
        show = (l == show_lock_idx or not show_only_one_lock)
        lock_pins = all_lock_pins[l]
        for k in blocked_keys_of_lock[l]:
            if k > max_fancy_blocked_keys: show = False
            if show: print("  Key", k, " vs Lock ", l," ------------------------------")
            key_cuts = all_key_cuts[k]
            blocked_somewhere = False
            for d, pins in zip(key_cuts, lock_pins):
                indicator = "   "
                if d not in pins:
                    blocked_somewhere=True
                    indicator = "   xxx"
                if show: print(f"    {d} {pins}".ljust(20) + indicator)
            if not blocked_somewhere:
                print("error, key can open other lock")
                return False
    return True


def verify_model(model):
    all_key_cuts = extract_key_cuts(model)
    all_lock_pins = extract_lock_pins(model)
    fancy_key_print(all_key_cuts)
    fancy_lock_print(all_lock_pins)

    ok = True
    ok &= verify_jumps(all_key_cuts)
    ok &= verify_open(all_lock_pins, all_key_cuts)
    ok &= verify_block(all_lock_pins, all_key_cuts)
    return ok

def write_model(output_lines):
    modelfile = instance_name + "_model.txt"
    with open(modelfile, "w") as f:
        for line in output_lines.splitlines():
            if line[0]=="v":
                f.write(line+"\n")

def write_solver_statistics(ouput_lines):
    statfile = instance_name + "_solverstats.txt"
    with open(statfile, "w") as f:
        for line in output_lines.splitlines():
            if line[0] in ["c","s"]:
                f.write(line + "\n")

if solve:
    SAT_STATUS, output_lines, model = solve_lockchart()
    write_solver_statistics(output_lines)

    print("\n \n \n")
    for line in output_lines.splitlines():
        if line[0] in ["c","s"]:
            print(line)

    if SAT_STATUS=="UNSAT":
        print("\n \nLockchart is unsatisfiable\n \n")
    else:
        ok = verify_model(model)
        write_model(output_lines)

    print("\nP",P,"  D",D,"  J",J,"  L",L,"  K",K)

    if SAT_STATUS =="SAT":
        if ok:
            print("\nLockchart verifier: All verifications passed!\n")
        else:
            print("\n \nERROR! Some key-lock verifications not passed, check above\n \n")

