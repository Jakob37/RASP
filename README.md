## RASP - Rapid Amplicon Sequence Pipeline

RASP is developed to aid study of metagenomic 16S rRNA datasets.
There are many powerful tools available for this type of analysis such as QIIME and Mothur.
Those often require significant effort to learn to use and to process the data with.

The purpose with RASP is to provide an intuitive and rapid platform for quickly and easily running
through your analysis. RASP is implemented together with a web interface, allowing anyone to run RASP
without neither downloads or installation procedures. You only need a browser, and your 16S amplicon
reads in gzipped FASTQ format.

http://mbio-serv2.mbioekol.lu.se/RASP

### Running RASP locally

Simple command for running RASP locally for two input files:

<pre>
./main.py --input_files file1.fastq.gz,file2.fastq.gz --input_labels sample1,sample2 --output_directory my_output_dir
</pre>

The installation procedure for RASP is not trivial, as it makes use of several programs and Python packages.
If using the web implementation is a viable alternative, I would recommend you to use that.

But if you want to run RASP locally, and are prepared for setting up some Linux dependencies, continue reading...

### Installation procedure

This procedure was tested on a freshly installed Ubuntu 16.04 computer.
It should be possible to run RASP on other Linux systems if you set up its dependencies properly, but the
exact installation procedure might differ from the one shown here.

##### Get RASP!

To retrieve the RASP source code, you can either clone the repository, or download it as a Zip through
the GitHub interface.

To clone the RASP repository, run the following:

<pre>
git clone https://Jakob37@bitbucket.org/jakobbioinformatics/rasp_pipeline
</pre>

##### Basic packages for environment

If not a root user, prefix the apt-get commands with sudo: "sudo apt-get install git".

Many of the dependencies here were necessary to run different components of RASP.
You can either run them one and one, or all together.

* git is needed to clone repositories from GitHub
* python3-pip is my preferred way to install Python3-packages. Python2-pip is pre-installed on Ubuntu 16.04.
* libpng-dev, libjpeg8-dev, libfreetype6-dev amd xvfb are dependencies for generating the Matplotlib graphics
* python-qt4 is needed to run the Python package ete2 used to visualize the phylogenetic tree
* default-jdk and ant are used for installation of RDP Classifier

To install all the dependencies at once, copy and paste the following into your terminal.

<pre>
apt-get install git python3-pip python-qt4 apt-get libpng-dev libjpeg8-dev libfreetype6-dev apt-get install xvfb default-jdk ant
</pre>

##### Setting up required Python packages

Unfortunately, currently both Python2 and Python3 is required to run RASP locally as software
like PyNAST only is available for Python2, while RASP is implemented in Python3.
Hopefully, the Python2 dependency can be dropped at a later point.

You need to have both pip2 and pip3 installed. Make sure to keep track of which version you are using.
The default "pip" command can refer to either version depending on your system. To
check which version it is, you can run:

<pre>
pip --version
</pre>

Python2 packages.

<pre>
# pip install numpy
# pip install pynast
pip install ete2
</pre>

Python3 packages

<pre>
pip3 install numpy
pip3 install matplotlib
pip3 install biopython
pip3 install scikit-bio
</pre>

### Retrieve software dependencies (and databases)

##### Prinseq (v0.20.4)

Prinseq is used to quality check the reads.
Download prinseq-lite standalone version from its download page.

https://sourceforge.net/projects/prinseq/files/standalone

After downloading, make the script executable and link it into the
RASP programs directory.

<pre>
cd prinseq_dir
chmod +x prinseq-lite.pl
cd ~/rasp_pipeline/Programs
ln -s ~/prinseq_dir/prinseq-lite.pl
</pre>

Finally setup the configuration file "settings.conf" to point to the correct name.

##### CD-HIT

CD-HIT is used for clustering similar sequences. It can be retrieved from:

https://github.com/weizhongli/cdhit

To compile, simply clone the repository and run 'make'.

<pre>
git clone https://github.com/weizhongli/cdhit.git
cd cdhit
make
</pre>

The binary named 'cd-hit-est' is used in RASP.

##### RDP Classifier

RDP Classifier is used for taxonomic assignment.

First, the RDP Tools were cloned:

<pre>
git clone https://github.com/rdpstaff/RDPTools.git
cd RDPTools
git submodule init
git submodule update
make
</pre>

This will generate the required jar-files used for classification.

RDP Classifier is per default trained for classification of 16S rRNA.

##### Vsearch

Vsearch performs reference based chimera checking of the OTUs.

Vsearch is present in the pre-packaged collection of software for Ubuntu / Debian.
If you want to run RASP on another system, get your own binary and place it appropriately:

https://github.com/torognes/vsearch

<pre>
sudo apt-get install dh-autoreconf

git clone https://github.com/torognes/vsearch
tar xf vsearch
cd vsearch
./autogen.sh
./configure
make
</pre>

##### PyNAST

PyNAST is a Python-package which wraps the NAST-aligner. It can be installed directly with
the Python package manager pip. It also requires us to download the software Uclust.

Uclust binaries are downloaded from http://www.drive5.com/uclust/downloads1_2_22q.html

<pre>
sudo apt-get install python-pip

wget http://www.drive5.com/uclust/uclustq1.2.22_i86linux64
mv uclustq1.2.22_i86linux64 uclust
chmod +x uclust

pip install numpy
pip install cogent
pip install pynast
</pre>

Navigate into the rasp_pipeline/Programs directory, and then link in the PyNAST.
In this case, the binary for PyNAST was located in the ~/.local/bin directory.

<pre>
cd ~/rasp_pipeline/Programs
ln -s ~/.local/bin/pynast
</pre>

##### FastTree

FastTree is used to build a tree-file from the NAST-alignment.

More information is found on http://www.microbesonline.org/fasttree

<pre>
wget http://www.microbesonline.org/fasttree/FastTree
</pre>

##### Databases

Currently RASP uses databases from GreenGenes for chimera checking, and NAST alignment.

The GreenGenes database

http://greengenes.secondgenome.com/downloads/database/13_5
http://www.mothur.org/w/images/2/21/Greengenes.gold.alignment.zip

// gg_13_5_pynast.fasta.gz (580MB) is used for PyNAST alignment.

* rRNA16S.gold.NAST_ALIGNED.fasta
* gg_13_5_otus.tar.gz (304 MB) is used for identifying chimeric sequences.

Note that the collection of Green Genes sequences is quite extensive.

<pre>
wget http://www.mothur.org/w/images/2/21/Greengenes.gold.alignment.zip
</pre>


### Citing RASP

### References

RASP couldn't possibly have been made possible without a number of software
that have been made available for public use. When using RASP, you use the software
outlined below too.

Prinseq
Schmieder R and Edwards R: Quality control and preprocessing of metagenomic datasets.
Bioinformatics 2011, 27:863-864. [PMID: 21278185]




