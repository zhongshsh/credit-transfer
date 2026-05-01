"""Map content claims to actual PDF page numbers in SYSU slide dumps."""
import re, sys, os
sys.stdout.reconfigure(encoding='utf-8')

DUMP = os.path.join(os.path.dirname(__file__), '_slices_dump')

queries = [
    ('SP09', r'Kendall', 'Kendall A/B/s notation'),
    ('SP09', r'PASTA', 'PASTA theorem'),
    ('SP09', r'Little', 'Little formula'),
    ('SP09', r'P_?block|阻塞|损失', 'M/M/s(k) blocking / Erlang-B'),
    ('SP09', r'M/M/s', 'M/M/s family'),
    ('SP09', r'M/M/1', 'M/M/1'),
    ('SP09', r'多服务|多排|T_1|T_2|T_3|单一|单队|分队', 'multi-server farm comparison'),
    ('SP08', r'Kolmogorov', 'Kolmogorov fwd/bwd equations'),
    ('SP08', r'生成元|Q.{0,3}矩阵|generator', 'Q generator'),
    ('SP08', r'M/M/1', 'M/M/1 in CTMC'),
    ('SP08', r'M/M/s', 'M/M/s in CTMC'),
    ('SP08', r'P_?block|阻塞|损失', 'M/M/s(k) blocking'),
    ('SP08', r'i\\ó|嵌入|jump chain|embedded', 'embedded jump chain'),
    ('SP04', r'memoryless|无记忆', 'memoryless property'),
    ('SP04', r'Erlang', 'Erlang interarrival'),
    ('SP05', r'splitting|分裂|分流|superposition|叠加', 'splitting/superposition'),
    ('SP05', r'conditional|条件', 'conditional uniformity'),
    ('SP06', r'recurrent|常返|transient|瞬', 'recurrent/transient'),
    ('SP06', r'period|周期', 'period of state'),
    ('SP06', r'Chapman.Kolmogorov|Chapman', 'C-K equation'),
    ('SP06', r'ergodic|遍历', 'ergodic class'),
    ('SP07', r'eigenvalue|特征值', 'eigenvalue analysis'),
    ('SP07', r'unichain|stationary|平稳', 'stationary / unichain'),
    ('SP14', r'Strong law', 'strong law for renewal'),
    ('SP14', r'renewal.reward|renewal-reward', 'renewal-reward general'),
    ('SP14', r'residual life|残.{0,3}寿|剩余寿命|excess', 'residual life'),
    ('SP15', r'Wald', 'Wald equality'),
    ('SP15', r'generalized stopping|generalized Wald', 'generalized Wald / stopping'),
    ('SP15', r'busy period|忙期', 'busy periods G/G/1'),
    ('SP15', r'Little.{0,3}[Tt]heorem|Theorem 5', 'Little theorem'),
    ('SP15', r'Pollaczek', 'Pollaczek-Khinchin'),
    ('SP15', r'M/G/1', 'M/G/1 derivation'),
    ('SP02', r'Monte Carlo', 'Monte Carlo simulation'),
    ('SP02', r'均匀.{0,5}产生|F_X|inverse|逆.{0,3}分布|6\.2', 'inverse-CDF method'),
    ('SP02', r'矩生成|moment generating|MGF', 'MGF'),
    ('SP03', r'Markov.{0,3}inequality|Markov 不等|马尔可夫', 'Markov inequality'),
    ('SP03', r'Chebyshev|切比雪夫', 'Chebyshev inequality'),
    ('SP03', r'Chernoff', 'Chernoff bound'),
    ('SP03', r'convergence|收敛', 'convergence modes'),
    ('SP10', r'Bellman|动态规划|DP', 'Bellman / DP'),
    ('SP11', r'finite horizon|有限', 'finite-horizon MDP'),
    ('SP12', r'infinite horizon|无穷|平均', 'infinite-horizon MDP'),
    ('SP13', r'reinforcement|RL|Q.{0,3}learning|policy iteration', 'RL / approximate DP'),
]

def compress(pages):
    if not pages: return ''
    ranges, start, prev = [], pages[0], pages[0]
    for p in pages[1:]:
        if p == prev + 1:
            prev = p
        else:
            ranges.append(str(start) if start == prev else f'{start}-{prev}')
            start = prev = p
    ranges.append(str(start) if start == prev else f'{start}-{prev}')
    return ','.join(ranges)

for label, pat, tag in queries:
    fp = os.path.join(DUMP, label + '.txt')
    with open(fp, encoding='utf-8') as f:
        text = f.read()
    parts = re.split(r'=== p(\d+) ===', text)
    pages = []
    for i in range(1, len(parts), 2):
        pno = int(parts[i])
        content = parts[i+1] if i+1 < len(parts) else ''
        if re.search(pat, content, re.I):
            pages.append(pno)
    rng = compress(pages)
    print(f'{label}  p.{rng:<18s}  {tag}')
