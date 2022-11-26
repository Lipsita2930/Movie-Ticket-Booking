import { Component, OnInit } from '@angular/core';
import {AfterViewInit, ViewChild} from '@angular/core';
import {MatPaginator} from '@angular/material/paginator';
import {MatSort} from '@angular/material/sort';
import {MatTableDataSource} from '@angular/material/table';
import { NavigationExtras, Router } from '@angular/router';
import { people } from '../Utilities/people';
import {MatButtonModule} from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { DialogComponent } from '../dialog/dialog.component';

@Component({
  selector: 'app-user-page',
  templateUrl: './user-page.component.html',
  styleUrls: ['./user-page.component.css']
})
export class UserPageComponent implements OnInit,AfterViewInit{
  displayedColumns: string[] = ['name', 'email','movieName','duration','price', 'noOfTickets', 'time','action'];
  dataSource:any;
 
  @ViewChild(MatPaginator, { static: false }) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  //variable declaration
    peopleTickets:people[]=[];
    table:any=[];
    data:any;
    
constructor(private router:Router,private dialog:MatDialog) { } 

  ngOnInit(): void {
    this.getPeopleTickets();
  }
  getPeopleTickets(){
    //getting the details from the localstorage  and storing it in table to show in the html
    this.peopleTickets.push(JSON.parse(localStorage.getItem('Users')||'{}'));
    this.table=this.peopleTickets[0];
    this.dataSource=new MatTableDataSource(this.table);
   }

  ngAfterViewInit() {
    this.dataSource.paginator=this.paginator;
    this.dataSource.sort=this.sort;
  }
  

 applyFilter(event: any) {
   const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
    let res = this.data.filter((v: {name:string}) => 
    v.name.toLowerCase().includes(filterValue.toLowerCase()) );
    this.dataSource = res;
    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }

  }


  onEditListener(row:any){
    this.dialog.open(DialogComponent,{
      data:row,
      width:'30%',
      id: 'dialogTrasparent',
      backdropClass: "bdrop",
    });
  }

}
