# Malaria Case Study
## Initialization
make sure conda installed
conda=
```bash=1
#login to server
ssh inf-49-2021@130.235.8.214
```
```bash=3
#make directory
mkdir Malaria
cd Malaria
```
## First Gene Prediction
GeneMark-ES/ET/EP ver 4.62_lic
```bash
#start with gene prediction 
mkdir 1_gene_predict/
cd 1_gene_predict/
#copy file from server file
cp /resources/binp29/Data/malaria/plasmodiumGenomes.tgz  .
#unzip
gzip -d plasmodiumGenomes.tgz
tar -xvf plasmodiumGenomes.tar
#geneMarker
#i chose to gene predict Plasmodium_yoelii
nohup gmes_petap.pl --ES --sequence Plasmodium_yoelii.genome & 
#change name
mv genemark.gtf Plasmodium_yoelii.gtf
#put file in shared folder
cp plasmodium_yoelii.gtf /tmp/Prediction/
```
## Genome Filtration

```bash
#genome clean
cd ..
mkdir 2_clean_genome/
cd 2_clean_genome/
#get file
cp /resources/binp29/Data/malaria/Haemoproteus_tartakovskyi.genome.gz .
gzip -d Haemoproteus_tartakovskyi.genome.gz 
#made cleaning.py python script
#python script 
python cleaning.py Haemoproteus_tartakovskyi.genome Haemoproteus_tartakovskyi_clean.genome

```

## Second Gene prediction

```bash=
#gene prediction again
cd ..
mkdir 3_gene_prediction/
cd 3_gene_prediction/
cp 2_clean_genome/Haemoproteus_tartakovskyi_clean.genome .
nohup gmes_petap.pl --ES --sequence 3_gene_prediction/Haemoproteus_tartakovskyi_clean.genome & 
#rename file
mv genemark.gtf Haemoproteus.gtf
```

## Blast

```bash=
#make directory
cd ..
mkdir 4_blast/
cd 4_blast/

#copy file from last directory
cp 3_gene_prediction/Haemoproteus.gtf .

#re format file for gffParse
cat Haemoproteus.gtf |sed -e 's/  length=.*\tGeneMark.hmm/\tGeneMark.hmm/' > Haemoproteus_2.gtf
#change from gtf to fasta
gffParse.pl -c -p -F -i Haemoproteus_tartakovskyi_clean.genome -g Haemoproteus_2.gtf 

#install blast
conda install blastp=2.12.0+
#blast
 blastp -query gffParse.faa -db SwissProt -evalue 1e-10 -out Ht.blastp -num_threads 16
```

## Bird Scaffolds Removal
```bash=
#find bird scaffolds
cd ..
mkdir 5_taxonomy/
cd 5_taxonomy/
#link databases
ln -s /resources/binp29/Data/malaria/taxonomy.dat taxonomy.dat
ln -s /resources/binp29/Data/malaria/taxonomy.dat uniprot_sprot.dat
cp 4_blast/Ht.blastp
cp 4_blast/gffParse.fna
cp 2_clean_genome/Haemoproteus_tartakovskyi_clean.genome .
python taxParser.py Ht.blastp taxonomy.dat uniprot_sprot.dat gffParse.fna Haemoproteus_tartakovskyi_clean.genome Haemoproteus_tartakovskyi.fna

```
## Third Gene Prediction 
```bash=
#redo gene prediction
cd ..
mkdir 6_gene_prediction/
cd 6_gene_prediction/
cp 5_taxonomy/Haemoproteus_no_bird.fna .
nohup gmes_petap.pl --ES --sequence 6_gene_prediction/Haemoproteus_tartakovskyi.fna & 
```

MISSING DATA

## Fasta Parse
```bash=
#make to fasta
cd ..
mkdir 7_make_fasta/
cd 7_make_fasta/
#change all names to Genus_species
mv Haemoproteus.gtf Haemoproteus_tartakovskyi.gtf
mv Haemoproteus_no_bird.fna Haemoproteus_tartakovskyi.genome
mv Tg.gff Toxoplasma_gondii.gtf
mv knowlesi.gtf Plasmodium_knowlesi.gtf
#fix Haemo...
cat Haemoproteus_tartakovskyi.gtf |sed -e 's/  length=.*\tGeneMark.hmm/\tGeneMark.hmm/' > Haemoproteus_tartakovskyi_2.gtf 
rm Haemoproteus_tartakovskyi.gtf 
mv Haemoproteus_tartakovskyi_2.gtf Haemoproteus_tartakovskyi.gtf
#for loop through all files
for file in *.gtf; do genus=$(echo $file | cut -c 1); species=$(echo $file | cut -d '_' -f 2 | cut -c 1 );genome=$(echo ${file%.gtf}.genome);gffParse.pl -c -p -F -i ${genus^^}${genome:1} -g $file -b ${genus^^}$species;done

```
## Ortholog Identification


```bash=
cp 7_make_fasta/*.faa 8_identify_orthologs/

conda create -n malaria
conda activate malaria
conda install proteinortho=6.0.33
nohup proteinortho6.pl {Ht,Pb,Pc,Pf,Pk,Pv,Py,Tg}.faa

 (CHECK)cat myproject.proteinortho.tsv | cut -f 1 | grep -c 8
 158
```

## BUSCOs

```bash=
#9_busco
cd ..
mkdir 9_busco
cd 9_busco

#took sooooooo long
conda update conda
conda install -c conda-forge -c bioconda busco=5.3.0
cp 7_make_fasta/*.faa 9_buscls/
for file in *.faa; do busco -i $file -o ${file%.faa} -m prot -l apicomplexa -f; done

```



##  Busco Ortholog Parse

```bash=
#for getting all the busco orthologs for each species
#making a file with all the BUSCOs found in all 8
cat concat_full_table.tsv | sort | uniq -c| grep " 8 " | cut -d " " -f 8 > busco_list.txt

#run buscoparser.py
python buscoparser.py busco_list.txt
```


## Alignment

```bash=
#10_alignment
cd ..
mkdir 10_alignment
cd 10_alignment
cp ../9_busco/Python_output/ .
#conda install
conda install -c bioconda clustalo=1.2.4 raxml=8.2.12
#make alignment directory
mkdir Alignment
#output alignment to Aligment directory
ls Python_output/* | while read file; do id=$(echo $file | sed s/Python_output// | tr -d '/' ); clustalo -i $file -o Alignment/$id -v ;done
#make tree directory
mkdir raxmlHPC_output
#now for for loop
 ls Alignment/* | while read file; do id=$(echo $file | sed s/Alignment// | tr -d '/' ); raxmlHPC -s $file -w /home/inf-49-2021/Malaria/10_alignment/raxmlHPC_output/ -n $id.tre -o Tg -m PROTGAMMABLOSUM62 -p 12345 ;done

```

## Tree Build

```bash=
#11_tree
cd ..
mkdir 11_tree
cd 11_tree
conda install -c bioconda phylip=3.698
#says it is already installed

cp -r  ../10_alignment/raxmlHPC_output/ .

rm raxmlHPC_output/RAxML_log.*
rm raxmlHPC_output/RAxML_parsimonyTree.*
rm raxmlHPC_output/RAxML_result.*
 rm raxmlHPC_output/RAxML_info.*
ls raxmlHPC_output/* | while read file; do cat $file >> intree ;done
phylip consense intree 
```










