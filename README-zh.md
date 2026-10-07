# 算术亚式期权的认证估值

**Theodore Ouyang**

[中文论文](paper/paper-zh.pdf) · [English paper](paper/paper.pdf) · [英文正文](manuscript/report.md)

论文利用共同高斯平滑得到加权 payoff 余项，并结合投影、变换反演、无限尾部和舍入误差，认证 Heston 模型与原始投影 Euler 离散模型之间的价格差。

对一年期、每月观察一次、执行价为95和110的算术亚式看涨价差，原参数点在 $`h=1/768`$ 时满足

```math
p_h-p_c\in[-0.011024692273,\;0.010642371599],
\qquad p_c\in[6.508371733,\;6.518868974].
```

原参数点完成了三个步长的证书；第二初始方差点完成了 $`h=1/768`$ 的证书。确定性方差例子的耦合非线性宽度约为分别估计宽度的 **0.573%**。这项比较只涉及该例的非线性分量。正波动率 Heston 点的耦合证书仍未完成。

九个 puts 与亚式价差的共同弱展开适用于 $`\xi=0`$；后验分位数位移界适用于论文指定的 $`\xi\in[10^{-7},10^{-6}]`$ 连续先验和合成报价。

## 复算与材料

从 [`paper` 标签](https://github.com/130U/certified-valuation-arithmetic-asian-options/tree/paper) 取得论文、代码及证据。

[原始模块](code/README.md) · [第二参数点与耦合例子](code/revision/round2/README.md) · [网格实验](code/revision/README.md) · [证据清单](EVIDENCE.md) · [构建说明](manuscript/FORMAT.md) · [审稿回应](REVIEW-RESPONSE-zh.md)

PDF 使用 ReportLab 与 MathJax 构建；仓库包含可编辑源文件、字体、依赖和构建记录。

研究与初稿写作于2023–2024年进行。2026年完成投稿前的整理与核验。

[theodore.oy2025@gmail.com](mailto:theodore.oy2025@gmail.com) · [10@alumni.duke.edu](mailto:10@alumni.duke.edu)
