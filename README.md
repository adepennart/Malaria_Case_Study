make sure conda installed
```bash=1
#login to server
ssh inf-49-2021@130.235.8.214
```
```bash=3
#make directory
mkdir Malaria
cd Malaria
```
## gene prediction 1
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
## genome clean

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

## gene prediction 2
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

## blast
```bash=
#blasting
cd ..
mkdir 4_blast/
cd 4_blast/
cp 3_gene_prediction/Haemoproteus.gtf .
#re format file for gffParse
cat Haemoproteus.gtf |sed -e 's/  length=.*\tGeneMark.hmm/\tGeneMark.hmm/' > Haemoproteus_2.gtf
#change from gtf to fasta
gffParse.pl -c -p -F -i Haemoproteus_tartakovskyi_clean.genome -g Haemoproteus_2.gtf 
#blast
 blastp -query gffParse.faa -db SwissProt -evalue 1e-10 -out Ht.blastp -num_threads 16
```

## remove bird scaffolds
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
python taxParser.py Ht.blastp taxonomy.dat uniprot_sprot.dat gffParse.fna Haemoproteus_tartakovskyi_clean.genome Haemoproteus_no_bird.fna

```
## gene prediction redo
```bash=
#redo gene prediction
cd ..
mkdir 6_gene_prediction/
cd 6_gene_prediction/
cp 5_taxonomy/Haemoproteus_no_bird.fna .
nohup gmes_petap.pl --ES --sequence 6_gene_prediction/Haemoproteus_no_bird.fna & 

```

MISSING DATA

## modify to fasta
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
## identify orthologs


```bash=
cp 7_make_fasta/*.faa 8_identify_orthologs/

conda create -n malaria
conda activate malaria
conda install proteinortho=6.0.33
nohup proteinortho6.pl {Ht,Pb,Pc,Pf,Pk,Pv,Py,Tg}.faa
```

## busco

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


## questions 7

```bash=
for file in *.faa; do count=$(cat ${file%.faa}/run_apicomplexa_odb10/full_table.tsv | grep -v '#'| grep -v "Missing"| grep -v "Fragmented" | cut -f 1 | sort -u | wc -l); echo ${file%.faa} $count ;done
# Ht 326
# Pb 372
# Pc 429
# Pf 436
# Pk 323
# Pv 437
# Py 434
# Tg 384

#no to see what percent are complete/ duplicate
for file in *.faa; do count=$(echo $(cat ${file%.faa}/run_apicomplexa_odb10/full_table.tsv |grep -v "#" | grep -v "Missing"| grep -v "Fragmented" | cut -f 1 | sort -u | wc -l)/ $(cat ${file%.faa}/run_apicomplexa_odb10/full_table.tsv | grep -v '#' |  cut -f 1 | sort -u | wc -l)|bc -l); echo ${file%.faa} $count ;done
# Ht .73094170403587443946
# Pb .83408071748878923766
# Pc .96188340807174887892
# Pf .97757847533632286995
# Pk .72421524663677130044
# Pv .97982062780269058295
# Py .97309417040358744394
# Tg .86098654708520179372
```

question 8 has no code requirement
## questions 9

```bash=
#make one concatonated file
for file in *.faa; do cat ${file%.faa}/run_apicomplexa_odb10/full_table.tsv | grep -v "#" | grep -v "Missing"| grep -v "Fragmented" | cut -f 1 | sort -u  >>concat_full_table.tsv ;done

#find BUSCO genes found in all 8
cat concat_full_table.tsv | sort | uniq -c| cut -d " " -f 7 | grep 8 | wc -l
# 185
#now for 7 species
#one contatonated file
ls *.faa | grep -v Tg.faa | while read file; do cat ${file%.faa}/run_apicomplexa_odb10/full_table.tsv | grep -v "#" | grep -v "Missing"| grep -v "Fragmented" | cut -f 1 | sort -u  >>7org_full_table.tsv ;done

```

## questions 10

```bash=
#now for 7 species
#one contatonated file
ls *.faa | grep -v Tg.faa | while read file; do cat ${file%.faa}/run_apicomplexa_odb10/full_table.tsv | grep -v "#" | grep -v "Missing"| grep -v "Fragmented" | cut -f 1 | sort -u  >>7org_full_table.tsv ;done

#find BUSCO found in all 7
cat 7org_full_table.tsv | sort | uniq -c| cut -d " " -f 7 | grep 7 | wc -l
204

```


## run buscoparser

```bash=
#for getting all the busco orthologs for each species
#making a file with all the BUSCOs found in all 8
cat concat_full_table.tsv | sort | uniq -c| grep " 8 " | cut -d " " -f 8 > busco_list.txt

#run buscoparser.py
python buscoparser.py busco_list.txt
```


## alignment

```bash=
#10_alignment
cd ..
mkdir 10_alignment
cd 10_alignment
cp ../9_busco/Python_output/ .
#conda install
conda install -c bioconda clustalo raxml
#make alignment directory
mkdir Alignment
#output alignment to Aligment directory
ls Python_output/* | while read file; do id=$(echo $file | sed s/Python_output// | tr -d '/' ); clustalo -i $file -o Alignment/$id -v ;done
#make tree directory
mkdir raxmlHPC_output
#now for for loop
 ls Alignment/* | while read file; do id=$(echo $file | sed s/Alignment// | tr -d '/' ); raxmlHPC -s $file -w /home/inf-49-2021/Malaria/10_alignment/raxmlHPC_output/ -n $id.tre -o Tg -m PROTGAMMABLOSUM62 -p 12345 ;done

```

## tree

```bash=
#11_tree
cd ..
mkdir 11_tree
cd 11_tree
conda install -c bioconda phylip
#says it is already installed
```









