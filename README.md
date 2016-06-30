## RASP - Rapid Amplicon Sequence Pipeline

RASP is developed to aid study of metagenomic 16S rRNA datasets.
There are many powerful tools available for this type of analysis such as QIIME and Mothur.
Those often require significant effort to learn to use and to process the data with.

The purpose with RASP is to provide an intuitive and rapid platform for quickly and easily running
through your analysis. It is implemented with a web interface, allowing processing without
any installation procedure. This is the recommended tool for most analyses.

http://mbio-serv2.mbioekol.lu.se/RASP

It is possible to run the RASP pipeline locally using the Python source found on this page.
It requires that you have several software and databases installed, but when you do have,
it can quickly and easily do the processing.

### Installation procedure

This procedure was tested on a freshly installed Ubuntu 16.04 computer.
RASP will run on other Linux systems if you set up its dependencies, but the
exact installation steps might vary.

Feel free to contact me if you run into trouble, preferably in the following forum:

FORUM

##### Basic packages for environment

If not a root user, prefix the apt-get commands with sudo: "sudo apt-get install git".

<pre>
apt-get install git

# Choose your preferred way to install python3-pip
apt-get install python3-pip

# Dependencies for matplotlib
apt-get libpng-dev libjpeg8-dev libfreetype6-dev

# This is used for rendering by matplotlib
# This means that the visualizations can be made on a system not running graphics
apt-get install xvfb

# Required for installation of RDP Classifier
sudo apt-get install default-jdk ant
</pre>

##### Setting up required Python packages

Unfortunately currently both Python2 and Python3 is required.
Make sure that you have both pip2 and pip3 installed.
Hopefully this can be remedied in the future.

<pre>
# Python2 packages
# pip install numpy
# pip install pynast
</pre>

<pre>
# Python3 packages
pip3 install matplotlib
</pre>

##### Clone the GitHub repository

Get RASP!

<pre>
git clone https://Jakob37@bitbucket.org/jakobbioinformatics/rasp_pipeline
</pre>

### Retrieve software dependencies (and databases)

##### Prinseq

Prinseq is used to quality check the reads.
Download prinseq-lite standalone version froum its download page.
For this guide, version 0.20.4 was used.

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

CD-HIT is used for clustering similar sequences into OTUs. It can be retrieved from:

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

###### Versions used

Cogent v1.9
Numpy v1.11.1
PyNAST v1.2.2

##### FastTree

FastTree is used to build a tree-file from the NAST-alignment. It is extremely fast, which made it
possible to include it in this pipeline.

More information is found on http://www.microbesonline.org/fasttree

<pre>
wget http://www.microbesonline.org/fasttree/FastTree
</pre>

##### Databases

Currently RASP uses databases from GreenGenes for chimera checking, and NAST alignment.
There are retrieved from the web page:

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




