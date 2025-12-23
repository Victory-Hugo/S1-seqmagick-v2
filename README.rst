=========
seqmagick2
==========
Version: 1.0.0
=========

.. image:: https://travis-ci.org/fhcrc/seqmagick2.svg?branch=master
    :target: https://travis-ci.org/fhcrc/seqmagick2

我们经常需要在不同格式之间转换序列文件并对其进行一些处理，
但为此编写脚本往往不值得。``seqmagick2`` 是一个强大的小工具，
可以以便捷的方式调用 BioPython 中的文件格式转换功能。
无需编写一堆脚本，只需一个接收参数的工具::

    seqmagick2 convert a.fasta b.phy    # 将 fasta 格式转换为 phylip 格式
    seqmagick2 mogrify --ungap a.fasta  # 从 a.fasta 中删除所有间隙，原地修改
    seqmagick2 info *.{fasta,sto}       # 描述当前目录中所有 FASTA 和 Stockholm
                                       # 文件的信息

需求
========

* Python >= 3.5
* biopython >= 1.78

快速安装
========

**推荐方式**：在 conda 环境中安装（避免污染系统 Python）::

   # 1. 创建 conda 环境（可选，推荐）
   conda create -n seqmagick python=3.9
   conda activate seqmagick

   # 2. 从 GitHub 直接安装
   pip install git+https://github.com/Victory-Hugo/S1-seqmagick-v2.git@v1.0.0

   # 3. 如果你已经安装过旧版本，建议先卸载再重新安装
   pip uninstall -y seqmagick2 
   pip install --no-cache-dir git+https://github.com/Victory-Hugo/S1-seqmagick-v2.git@v1.0.0


如果上述命令无法工作，您可以手动克隆后安装::

   git clone https://github.com/Victory-Hugo/S1-seqmagick-v2.git@v1.0.0
   cd S1-seqmagick-v2
   pip install -e .

**注意**：请确保在目标 Python 环境中运行 pip 命令。如果使用 conda，先激活环境再安装。


功能特性
========

* 修改序列：删除间隙、反向互补、反向、改变大小写、

  - 删除间隙
  - 反向和反向互补
  - 修剪到指定的残基范围
  - 改变大小写
  - 按长度或 ID 排序
  - `更多`_

* 显示序列文件的 `信息 <http://seqmagick2.readthedocs.org/en/latest/info.html>`_
* 通过以下方式对序列文件进行子集化：

  - 位置
  - ID
  - 去重复
  - `更多`_

* 通过 `质量分数 <http://seqmagick2.readthedocs.org/en/latest/quality_filter.html>`_ 过滤序列
* 将比对序列修剪到由正向和反向引物定义的 `感兴趣区域 <http://seqmagick2.readthedocs.org/en/latest/primer_trim.html>`_

想了解更多？前往 `文档`_。

``seqmagick2`` 是 GPL v3 下的自由软件。


.. _`文档`: http://seqmagick2.readthedocs.org/en/latest/

.. _`更多`: http://seqmagick2.readthedocs.org/en/latest/convert_mogrify.html
