Changes for seqmagick2
=====================

0.8.0
-----

* Supports Python 3.5+
* Drops support for Python 3.4
* Fix issue: "seqmagick2 with no params gives KeyError:None" [GH-77]
* Fix for Biopython 1.71 dual coding support [GH-76]; also fixes issue: "Translation error with new BioPython" [GH-79]
* Send logging to stderr, not stdout [GH-75]

0.7.0
-----

* Supports Python 3.4+
* Drops support for python 2.7
* requires biopython >= 1.70
* Drops support for bz2 compression [see GH-66]
* New option ``convert --sample-seed`` to make ``--sample`` deterministic.

0.6.2
-----

* New ``quality-filter --pct-ambiguous`` switch [GH-53]
* setup.py enforces biopython>=1.58,<=1.66 (1.67 is not compatible) [GH-59]
* This is the last release that will support Python 2!

0.6.1
-----

* Allow string wrapping when input isn't FASTA. [GH-45]
* Fix ``--pattern-include``, ``--pattern-exclude``, and ``--pattern-replace``
  for sequences without descriptions (e.g., from NEXUS files). [GH-47]
* Fix mogrify example. [GH-52]

0.6.0
-----

* Map ``.nex`` extension to NEXUS-format (--alphabet must be specified if writing)
* Use reservoir sampling in ``--sample`` selector (lower memory use)
* Support specifying negative indices to ``--cut`` [GH-33]
* Optionally allow invalid codons in ``backtrans-align`` [GH-34]
* Map ``.fq`` extension to FASTQ format
* Optional multithreaded I/O in ``info`` [GH-36]
* Print sequence name on length mismatch in ``backtrans-align`` [GH-37]
* Support for ``+`` and ``-`` in head and tail to mimick Linux head and tail commands.
* Fix scoring for mixed-case sequences in ``primer-trim``.
* Fix bug in ``primer-trim`` - failed when sequence had multiple 5' gaps compared to the primer.
* Clarify documentation and fix bug in convert/mogrify ``--pattern-replace`` [GH-39]
* Support for gzip files in ``seqmagick2 convert --sort``

0.5.0
-----

* Change ``seqmagick2 extract-ids --source-format`` to ``--input-format`` to match
  other commands (GH-29)
* Support gzip- and bzip2-compressed inputs and outputs for most commands (GH-30)
* Change default input format for ``sff`` to ``sff-trim``, which respects the
  clipping locations embedded in each sequence record.
* Add ``--details-out`` option to ``seqmagick2 quality-filter``, which writes
  details on each read processed.
* Match barcode/primer ``seqmagick2 quality-filter`` against a trie; allows
  per-specimen barcodes.
* Remove ``--failure-out`` option from ``seqmagick2 quality-filter``. See ``--details-out``
* Raise an error if number of codons does not match number of amino acids in
  ``seqmagick2 backtrans-align``
* Add ``--sample`` subcommand (GH-31)

0.4.0
-----

* Fix bug in ``--squeeze``
* More informative messages in ``seqmagick2 primer-trim``
* Added ``--alphabet`` flag to allow writing NEXUS (GH-23)
* Exiting without error on SIGPIPE in extract-ids, info (GH-17)
* Ambiguities are translated as 'X' in --translate (GH-16)
* Allowing '.' or '-' as gap character (GH-18)
* ``--name-prefix`` and ``--name-suffix`` no longer create a mangled description (GH-19)
* Files owned by another user can be mogrified, as long as they are group writeable (GH-14)
* Add ``backtrans-align`` subcommand, which maps unaligned nucleotides onto a
  protein alignment (GH-20)
* Allow FASTQ as input to quality-filter
* Significantly expand functionality of quality-filter: identify and trim
  barcodes/primers; report detailed failure information.
* Cleanup, additional tests
* Add ``--drop`` filter to convert and mogrify (GH-24)
* Apply current umask when creating files (GH-26)
* Support stdin in ``seqmagick2 info`` (GH-27)
* Support translating ambiguous nucleotides, if codon translation is unambiguous

0.3.1
-----

* Fix bug in ``quality-filter`` MinLengthFilter
* Case consistency in seqmagick2

0.3.0
-----

* Internal reorganization - transformations are converted to partial functions,
  then applied.
* Argument order now affects order of tranformation application.
* Change default output format to 'align' for TTYs in seqmagick2 info
* Add BioPython as dependency (closes GH-7)
* Add ``primer-trim`` subcommand
* Add option to apply custom function(s) to sequences
* Add new filtering options: ``--squeeze-threshold``, ``--min-ungapped-length``
  ``--include-from-file`` ``--exclude-from-file``
* Removed seqmagick2 muscle
* Added new subcommand ``quality-filter``
* Added new subcommand ``extract-ids`` (closes GH-13)
* Allow use of '-' to indicate stdin / stdout (closes GH-11)
* Add mapping from .phyx to ``phylip-relaxed`` (targeted for BioPython 1.58)

0.2.0
-----

* Refactoring
* Added hyphenation to multi-word command line options (e.g.
  ``--deduplicatetaxa`` -> ``--deduplicate-taxa``)
* Add support for ``.needle``, ``.sff`` formats
* Close GH-4

0.1.0
-----
Initial release
