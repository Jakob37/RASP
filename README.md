# RASP - Rapid Amplicon Sequence Pipeline

## Table of Content

* [Introduction](#introduction)
* [Running RASP locally](#running-rasp-locally)
* [Installation procedure](#installation-procedure)
  * [Installing apt-get packages](#installing-apt-get-packages)
  * [Installing Python packages](#installing-python-packages)
  * [Databases](#databases)
  * [Setting up RASP](#setting-up-rasp)
  * [Testing installation](#testing-installation)
* [Citing RASP](#citing-rasp)
* [References](#references)

## Introduction

RASP is developed to aid and simplify the study of metagenomic 16S rRNA sequence data.
There are powerful tools available for this type of analysis where two of the more notable are
QIIME and Mothur. These tools often require significant effort to learn to use and to process the data with,
especially if you have no prior terminal experience.

The purpose with RASP is to act as a complementary tool providing a quick and intuitive
alternative for performing a core analysis of your samples.
Currently, RASP provides the following analysis:

* Quality control and filtering of reads
* Clustering of reads into OTUs
* Taxonomic classification of OTUs
* Chimera checking the OTUs
* Visualization of taxonomic composition of the different samples
* Calculation and visualization of alpha-diversity indices for each sample
* Generation and visualization of a phylogenetic tree

RASP is implemented together with a web interface, allowing anyone to run RASP
without neither downloads or installation procedures. Here, you can easily upload your samples,
and later see and download the results of the processing. You only need a browser and your 16S amplicon
reads in gzipped FASTQ format.

http://mbio-serv2.mbioekol.lu.se/RASP

This is the recommended and easiest way of using RASP.

RASP expects your reads to be without barcode or primer sequences. If you are working with paired-end
reads it is recommended to merge them before analysis. A good tool for merging paired-end reads is PandaSeq:
https://github.com/neufeld/pandaseq

RASP can also be run locally, and when installed the full analysis can be executed locally by a single command.
Be aware though that the installation procedure takes some effort due to the many dependencies of RASP.
If you are ready to get your hands dirty with some terminal-work, continue reading.

If you run into trouble, feel free to write me a line:

jakob (dot) willforss (at) gmail (dot) com

## Running RASP locally

After setting up its dependencies, RASP can be run from the terminal in the following way:

<pre>
./main.py --input_files file1.fastq.gz,file2.fastq.gz --input_labels sample1,sample2 --output_directory my_output_dir
</pre>

Input arguments:

<pre>
usage: main.py [-h] --input_files INPUT_FILES --input_labels INPUT_LABELS
               --output_directory OUTPUT_DIRECTORY
               [--otu_filter_threshold OTU_FILTER_THRESHOLD]
               [--otu_cluster_identity OTU_CLUSTER_IDENTITY]
               [--pynast_identity PYNAST_IDENTITY]
               [--rdp_identity RDP_IDENTITY] [--rdp_database RDP_DATABASE]
               [--rdp_depth {phylum,class}] [--tree_software {fasttree,raxml}]
               [--chimera_checking {none,vsearch}]

optional arguments:
  -h, --help            show this help message and exit
  --input_files INPUT_FILES
                        Comma-delimited input files (requires gzipped FASTQ
                        format)
  --input_labels INPUT_LABELS
                        Comma-delimited labels for the input files
                        (sample1,sample2...)
  --output_directory OUTPUT_DIRECTORY
                        The output directory
  --otu_filter_threshold OTU_FILTER_THRESHOLD
                        OTUs with lower counts are removed. Artifacts are more
                        common in low-count clusters especially for singletons
                        (clusters consisting of a single read)
  --otu_cluster_identity OTU_CLUSTER_IDENTITY
                        Reads with higher or equal similarity to this
                        threshold are clustered into an OTU 0.97 is commonly
                        used as a proxy for prokaryotic species Must have a
                        value between 0.8 and 1.0 (inclusive)
  --pynast_identity PYNAST_IDENTITY
                        Threshold for the OTU sequence alignment quality used
                        for inclusion of the OTU in the phylogenetic tree Can
                        be used to prevent outliers, but will if set to non-
                        zero lead to that some OTUs present in the other
                        analyses will be missing in the tree Must have a value
                        between 0.0 and 1.0 (inclusive)
  --rdp_identity RDP_IDENTITY
                        Threshold for the RDP Classifier certainty when
                        assigning a taxon If below threshold the OTU sequence
                        is discarded0.8 is commonly usedMust have a value
                        between 0.5 and 1.0 (inclusive)
  --rdp_database RDP_DATABASE
                        RDP classification database (currently only 16S
                        implemented)
  --rdp_depth {phylum,class}
                        RDP classification depth
  --tree_software {fasttree,raxml}
                        Software used for tree generation RAxML can be
                        slightly more accurate but results in drastically
                        slower analysis
  --chimera_checking {none,vsearch}
                        Filters sequences assigned as chimeric by reference
                        based chimera checking performed by Vsearch
</pre>

## Installation procedure

This procedure was tested on a freshly installed Ubuntu 16.04 computer.
It should be possible to run RASP on other Linux systems, but the
exact installation procedure for the different dependencies might differ from the one shown here.

To retrieve the RASP source code, you can either clone the repository, or download it as a Zip through
the GitHub interface.

To clone the RASP repository, you need to have Git installed. For the apt-get commands, you will likely
need to run as an elevated user which is done by prefixing the command with sudo: "sudo apt-get install git".

<pre>
apt-get install git
</pre>

Now we can clone the repository.

<pre>
git clone https://github.com/Jakob37/RASP.git
</pre>

#### Installing apt-get packages

The following dependencies were needed to get it running on Ubuntu.

To install all the dependencies at once, copy and paste the following into your terminal
(don't forget the sudo if you need to run as an elevated user).

<pre>
apt-get install python-pip python3-pip python-qt4 libpng-dev libjpeg8-dev libfreetype6-dev xvfb default-jdk ant dh-autoreconf openmpi-bin
</pre>

Note: After installation these packages uses around 300MB disk space.

#### Installing Python packages

Unfortunately, currently both Python2 and Python3 is required to run RASP locally.
Some software used by RASP is still dependent on Python2, while RASP is built in Python3.
Hopefully, the Python2-dependencies will be replaced at some point.

You need to have both pip2 and pip3 installed (package managers for Python2 and Python3) to follow
this tutorial. Make sure to keep track of which version you are using.
The default "pip" command can refer to either version depending on your system. To
check which version it is, you can run:

<pre>
pip --version
</pre>

Install needed Python2 packages:

<pre>
pip2 install numpy
pip2 install cogent
pip2 install ete2
</pre>

Install needed Python3 packages:

<pre>
pip3 install numpy
pip3 install matplotlib
pip3 install biopython
pip3 install scikit-bio
</pre>

### Installing required software and databases

RASP uses the following external software:

* Prinseq
* CD-HIT
* RDP Classifier
* Vsearch
* PyNAST
* FastTree

The software can either be set up directly in a directory named "Programs" within the
RASP directory, or they can be linked into this directory after setting up the programs
elsewhere. Here, the programs will be downloaded and set up in the home/bin directory.
In the end, they are linked into the "Programs" directory, and the configuration file is
adjusted accordingly.

##### Prinseq

Prinseq is used to exclude low quality reads and for trimming of low quality ends.
Download prinseq-lite standalone version from its download page.
For this guide, version 0.20.4 was used.

https://sourceforge.net/projects/prinseq/files/standalone

<pre>
mkdir ~/src
mv ~/Downloads ~/src
cd ~/src
tar xf prinseq-lite-0.20.4.tar.gz
chmod +x prinseq-lite-0.20.4/prinseq-lite.pl
</pre>

Here, the downloaded Prinseq directory is extracted in ~/src, and the prinseq-lite.pl script
is made executable. It will later be linked into RASP's Programs folder.

##### CD-HIT

CD-HIT is used for clustering similar sequences. Its GitHub repository is found at:

https://github.com/weizhongli/cdhit

To compile, simply clone the repository and run 'make'.

<pre>
cd ~/src
git clone https://github.com/weizhongli/cdhit.git
cd cdhit
make
</pre>

The binary named 'cd-hit-est' is later used in RASP.

##### RDP Classifier

RDP Classifier is used for taxonomic assignment, and is out of the box trained on
16S rRNA sequences. Its GitHub repository is found at:

https://github.com/rdpstaff/RDPTools.git

<pre>
cd ~/src
git clone https://github.com/rdpstaff/RDPTools.git
cd RDPTools
git submodule init
git submodule update
make
</pre>

This will generate the required jar-files used for classification.
This is quite size-demanding, and requires around 700 MB disk space.

The jar-file classifier.jar is later used in RASP.

##### Vsearch

Vsearch is an open-source re-implementation of the well known Usearch suite.
RASP uses Vsearch to perform reference based chimera checking of the OTUs.
Its GitHub repository is found at:

https://github.com/torognes/vsearch.git

<pre>
cd ~/src
git clone https://github.com/torognes/vsearch.git
cd vsearch
./autogen.sh
./configure
make
</pre>

We will be using the binary "vsearch" found in vsearch/bin in RASP.

##### PyNAST

PyNAST is a Python-package which wraps the NAST-aligner. It can be installed directly with
the Python package manager pip. It also requires us to download the software Uclust.
This is in my experience the software for which the installation is the most error-prone.

Uclust binary is downloaded from http://www.drive5.com/uclust/downloads1_2_22q.html

The Uclust binary is only allowed to be used together with PyNAST or QIIME.

To run PyNAST, the Uclust binary needs to be accessible through the PATH, and named simply 'uclust'.

<pre>
cd ~/src
wget http://www.drive5.com/uclust/uclustq1.2.22_i86linux64
mkdir ~/bin
cp uclustq1.2.22_i86linux64 ~/bin/uclust
chmod +x ~/bin/uclust
</pre>

General installation instructions for PyNAST can be found here:

http://biocore.github.io/pynast/install.html

In this case we install it through pip2. Note that we previously installed the dependencies
"numpy" and "cogent".

<pre>
pip2 install pynast
</pre>

On this computer, the pynast binary ended up in the ~/.local/bin/pynast directory.
This is the binary which will be used in this installation setup.

There are other ways of installing PyNAST. Feel free to give them a go. This was the one
that worked out for me.

##### FastTree

FastTree is used to build a tree-file from the NAST-alignment.

More information is found on http://www.microbesonline.org/fasttree

The FastTree binary can be obtained directly from the web page.

<pre>
cd ~/bin
wget http://www.microbesonline.org/fasttree/FastTree
chmod +x FastTree
</pre>

That was all the software. Now, it is only the databases left.

### Databases

Currently RASP uses databases for the following processing steps:

* Chimera checking
* Building NAST alignment
* Taxonomic classification

Both RDP and GreenGenes provide their databases under a Creative Commons
Attribution-ShareAlike 3.0 license (https://creativecommons.org/licenses/by-sa/3.0/).

#### Chimera checking database

It is recommended to use a small high-quality database for chimera checking.
Here, we are using the latest version of RDP Classifier's training dataset.
It can downloaded from the following page:

https://sourceforge.net/projects/rdp-classifier/files/RDP_Classifier_TrainingData/

In this case, version 15 (RDPClassifier_16S_trainsetNo15_rawtrainingdata.zip) was used.

<pre>
mkdir ~/databases
cd ~/databases
mv ~/Downloads/RDPClassifier_16S_trainsetNo15_rawtrainingdata.zip ~/databases/
unzip RDPClassifier_16S_trainsetNo15_rawtrainingdata.zip
</pre>

We will use the trainset15_092015.fa which contains 11127 entries.

#### PyNAST alignment database

A PyNAST aligned database can be downloaded from the GreenGenes database at:

http://greengenes.secondgenome.com/downloads/database/13_5

The full PyNAST alignment is too large to work with. For now, we are using the
GreenGenes alignment of a RDP gold subset.

<pre>
cd ~/databases
wget http://www.mothur.org/w/images/2/21/Greengenes.gold.alignment.zip
unzip Greengenes.gold.alignment.zip
</pre>

This database contains 5181 sequences.

### Setting up RASP

Now, we should have all the dependencies in place and all the databases available. The final step
is to tell RASP where to look for all of these dependencies.

RASP looks into the folder "Programs" for programs and the folder "Databases" for databases.
Edit the file "settings.conf" to tell RASP exactly what to look for.

Here, I will first create links from those directories to the retrieved software / databases,
and then update the configuration file.

<pre>
mkdir ~/rasp_pipeline/Programs
cd ~/rasp_pipeline/Programs

ln -s ~/src/FastTree
ln -s ~/src/cdhit/cd-hit-est
ln -s ~/src/prinseq-lite-0.20.4/prinseq-lite.pl
ln -s ~/src/vsearch/bin/vsearch
ln -s ~/.local/bin/pynast
ln -s ~/src/RDPTools/classifier.jar
</pre>

Next, let's prepare the databases.

<pre>
mkdir ~/rasp_pipeline/Databases
cd ~/rasp_pipeline/Databases

ln -s ~/databases/RDPClassifier_16S_trainsetNo15_rawtrainingdata/trainset15_092015.fa
ln -s ~/databases/rRNA16S.gold.NAST_ALIGNED.fasta
</pre>

Finally, edit "settings.conf" to match our programs. Use "settings_template.conf" as a starting point, and fill in
the software.

<pre>
cd ~/rasp_pipeline
cp settings_template.conf settings.conf
</pre>

After editing my settings.conf looked
like the following (leave the other parts as they are):

<pre>
[basepaths]
scripts=Scripts/
programs=Programs/
databases=Databases/

[programs]
prinseq                 = prinseq-lite.pl
vsearch                 = vsearch
cdhit                   = cd-hit-est
rdpclassifier           = classifier.jar
fasttree                = FastTree
pynast                  = pynast

[databases]
pynast_16S              = rRNA16S.gold.NAST_ALIGNED.fasta
uchime_16S_ref          = RDPClassifier_16S_trainsetNo15_rawtrainingdata
</pre>

### Testing installation

To evaluate the installation, run the test suite in the folder TestRun.

<pre>
cd ~/rasp_pipeline/TestRun/
./verify_setup.py
</pre>

This will give you information about whether the pipeline crashed, and if so, at what stage.
To find out further details, open the rasp.err log found in TestRun/output_files.

If you run into problems during your installation - Send me an email, and we will see whether we can figure it out.
The most likely reason for a crash is that one of the dependencies of RASP isn't working properly.

## Citing RASP

RASP is currently not published, but a manuscript is on its way.

## References

RASP couldn't possibly have been made possible without a number of software
that have been made available for public use. When using RASP, you use the software
outlined below too.

### Programs

##### Prinseq

Schmieder, R., and Edwards. R. (2011).
Quality control and preprocessing of metagenomic datasets.
*Bioinformatics*, **27**, 863-864. doi:10.1093/bioinformatics/btr026

##### CD-HIT

Fu, L., Niu, B., Zhu, Z., Wu, S. and Li, W. (2012).
CD-HIT: accelerated for clustering the next generation sequencing data.
*Bioinformatics*, **28**, 3150-3152. doi: 10.1093/bioinformatics/bts565

Li, W. and Godzik, A. (2006).
Cd-hit: a fast program for clustering and comparing large sets of protein or nucleotide sequences.
*Bioinformatics*, **22**, 1658-1659. doi: 10.1093/bioinformatics/btl158

##### FastTree

Price, M.N., Dehal, P.S., and Arkin, A.P. (2009).
FastTree: Computing Large Minimum-Evolution Trees with Profiles instead of a Distance Matrix.
*Molecular Biology and Evolution*, **26**, 1641-1650. doi:10.1093/molbev/msp077

##### RDP Classifier

Wang, Q, G. M. Garrity, J. M. Tiedje, and J. R. Cole. (2007).
Naïve Bayesian Classifier for Rapid Assignment of rRNA Sequences into the New Bacterial Taxonomy.
*Appl. Environ. Microbiol.*, **73**, 5261-5267, doi: 10.1128/AEM.00062-07

##### PyNAST

Caporaso, J. G., Bittinger, K., Bushman, F. D., DeSantis, T. Z., Andersen, G. L., & Knight, R. (2010).
PyNAST: a flexible tool for aligning sequences to a template alignment.
*Bioinformatics*, **26**, 266–267. doi: 10.1093/bioinformatics/btp636

##### RAxML

RAxML is only used if you change the default settings for the tree software.

Stamatakis, A. (2014).
RAxML version 8: a tool for phylogenetic analysis and post-analysis of large phylogenies.
*Bioinformatics*, **30**, 1312–1313. doi: 10.1093/bioinformatics/btu033

##### Vsearch

GitHub repository: https://github.com/torognes/vsearch

### Databases

#### RDP databases

Cole, J.R. *et al*. (2014). 
Ribosomal Database Project: data and tools for high throughput rRNA analysis.
*Nucl. Acids Res.*, **42**, 633-642. doi: 10.1093/nar/gkt1244

#### GreenGenes database

DeSantis, T.Z. *et al*. (2006). 
Greengenes, a Chimera-Checked 16S rRNA Gene Database and Workbench Compatible with ARB.
*Appl. Environ. Microbiol.*, **72**, 5069-5072. doi: 10.1128/AEM.03006-05

### Python packages

The following Python packages play a central role in RASP's visualizations and calculations.

##### Matplotlib

Matplotlib is used to make the majority of RASP's visualizations.

Hunter, J. D. (2007). 
Matplotlib: A 2D Graphics Environment
*Science & Engineering*, **9**, 90-95. doi: 10.1109/MCSE.2007.55

##### ETE toolkit

The ETE toolkit is used to visualize the phylogenetic tree generated by RASP.

Huerta-Cepas, J. Dopazo, J. and Gabaldon, Toni. (2010). 
ETE: a python Environment for Tree Exploration.
*BMC Bioinformatics*, **11**:24. doi: 10.1186/1471-2105-11-24

##### Sci-kit bio

Sci-kit bio is used for calculating diversity indices.

GitHub repository: https://github.com/biocore/scikit-bio
