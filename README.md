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
#make directory
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
#Make directory
cd ..
mkdir 2_clean_genome/
cd 2_clean_genome/

#copy file from previous folder
cp /resources/binp29/Data/malaria/Haemoproteus_tartakovskyi.genome.gz .
gzip -d Haemoproteus_tartakovskyi.genome.gz 

#run python script 
python cleaning.py Haemoproteus_tartakovskyi.genome Haemoproteus_tartakovskyi_clean.genome

```

## Second Gene Prediction

```bash=
#make directory
cd ..
mkdir 3_gene_prediction/
cd 3_gene_prediction/

#copy file from previous directory
cp 2_clean_genome/Haemoproteus_tartakovskyi_clean.genome .

#gene prediction
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

#copy file from previous directory
cp 3_gene_prediction/Haemoproteus.gtf .

#re format file for gffParse
cat Haemoproteus.gtf |sed -e 's/  length=.*\tGeneMark.hmm/\tGeneMark.hmm/' > Haemoproteus_2.gtf
#change from gtf to fasta
gffParse.pl -c -p -F -i Haemoproteus_tartakovskyi_clean.genome -g Haemoproteus_2.gtf 

#install blast
conda install bioconda blast=2.12.0+

#blast
 blastp -query gffParse.faa -db SwissProt -evalue 1e-10 -out Ht.blastp -num_threads 16
```

## Bird Scaffolds Removal
```bash=
#make directory
cd ..
mkdir 5_taxonomy/
cd 5_taxonomy/

#link databases
ln -s /resources/binp29/Data/malaria/taxonomy.dat taxonomy.dat
ln -s /resources/binp29/Data/malaria/taxonomy.dat uniprot_sprot.dat

#copy files from previous directory
cp 4_blast/Ht.blastp
cp 4_blast/gffParse.fna
cp 2_clean_genome/Haemoproteus_tartakovskyi_clean.genome .

#run python script
python taxParser.py Ht.blastp taxonomy.dat uniprot_sprot.dat gffParse.fna Haemoproteus_tartakovskyi_clean.genome Haemoproteus_tartakovskyi.fna

```
## Third Gene Prediction 
```bash=
#make directory
cd ..
mkdir 6_gene_prediction/
cd 6_gene_prediction/

#copy file from previous directory
cp 5_taxonomy/Haemoproteus_tartakovskyi.fna .

#gene prediction
nohup gmes_petap.pl --ES --sequence 6_gene_prediction/Haemoproteus_tartakovskyi.fna & 
#rename file
mv genemark.gtf Haemoproteus.gtf

```

## Fasta Parse
```bash=
#make directory
cd ..
mkdir 7_make_fasta/
cd 7_make_fasta/

#copy Haemoproteus_tartakovskyi from previous directory, others from shared folder
cp 6_gene_prediction/Haemoproteus_tartakovskyi.fna . 
cp 6_gene_prediction/Haemoproteus.gtf .
cp /tmp/Prediction/*

#change all names to Genus_species
mv Haemoproteus.gtf Haemoproteus_tartakovskyi.gtf
mv Haemoproteus_tartakovskyi Haemoproteus_tartakovskyi.genome
mv Tg.gff Toxoplasma_gondii.gtf
mv knowlesi.gtf Plasmodium_knowlesi.gtf

#reformat Haemoproteus_tartakovskyi.gtf
cat Haemoproteus_tartakovskyi.gtf |sed -e 's/  length=.*\tGeneMark.hmm/\tGeneMark.hmm/' > Haemoproteus_tartakovskyi_2.gtf 
rm Haemoproteus_tartakovskyi.gtf 
mv Haemoproteus_tartakovskyi_2.gtf Haemoproteus_tartakovskyi.gtf

#for loop through all files
for file in *.gtf; do genus=$(echo $file | cut -c 1); species=$(echo $file | cut -d '_' -f 2 | cut -c 1 );genome=$(echo ${file%.gtf}.genome);gffParse.pl -c -p -F -i ${genus^^}${genome:1} -g $file -b ${genus^^}$species;done

```
## Ortholog Identification

```bash=
#make directory
cd ..
mkdir 8_identify_orthologs
cd 8_identify_orthologs

#copy files from previous directory
cp 7_make_fasta/*.faa 8_identify_orthologs/

# make conda environment for installing software
conda create -n malaria
conda activate malaria
conda install proteinortho=6.0.33

#find orthologs
nohup proteinortho6.pl {Ht,Pb,Pc,Pf,Pk,Pv,Py,Tg}.faa

```

## BUSCOs

```bash=
#make directory
cd ..
mkdir 9_busco
cd 9_busco

#update conda for busco=5.3.0 install
conda update conda
conda install -c conda-forge -c bioconda busco=5.3.0

#copy file from previous directory
cp 7_make_fasta/*.faa 9_buscls/

#for loop find busco genes
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
#make directory
cd ..
mkdir 10_alignment
cd 10_alignment

#copy file directory from previous directory
cp ../9_busco/Python_output/ .

#conda install software
conda install -c bioconda clustalo=1.2.4 raxml=8.2.12

#make alignment directory
mkdir Alignment

#output alignment to Aligment directory
ls Python_output/* | while read file; do id=$(echo $file | sed s/Python_output// | tr -d '/' ); clustalo -i $file -o Alignment/$id -v ;done

#make tree directory
mkdir raxmlHPC_output

#now  for loop making trees
 ls Alignment/* | while read file; do id=$(echo $file | sed s/Alignment// | tr -d '/' ); raxmlHPC -s $file -w /home/inf-49-2021/Malaria/10_alignment/raxmlHPC_output/ -n $id.tre -o Tg -m PROTGAMMABLOSUM62 -p 12345 ;done

```

## Tree Build

```bash=
#make directory
cd ..
mkdir 11_tree
cd 11_tree

#install software
conda install -c bioconda phylip=3.698

#copy directory from previous directory
cp -r  ../10_alignment/raxmlHPC_output/ .

#keep on besttree files
rm raxmlHPC_output/RAxML_log.*
rm raxmlHPC_output/RAxML_parsimonyTree.*
rm raxmlHPC_output/RAxML_result.*
rm raxmlHPC_output/RAxML_info.*

#concatonate files
ls raxmlHPC_output/* | while read file; do cat $file >> intree ;done

#run software
phylip consense intree 
#say yes to options

#copy output files to computer
scp out* inf-49-2021@bioinf-biol302449.biol.lu.se:~ 

#install figtree
conda install figtree=v1.4.4

#run figtree to display tree
figtree outtree
```










