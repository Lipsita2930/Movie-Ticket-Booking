import { ThisReceiver } from '@angular/compiler';
import { Component, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, NavigationExtras } from '@angular/router';
import { UserService } from '../Services/user.service';
import { Movies } from '../Utilities/Movie';
import {MatDialog, MatDialogModule} from '@angular/material/dialog';
import { DialogComponent } from '../dialog/dialog.component';
import { SharedService } from '../Services/shared.service';


@Component({
  selector: 'app-movie-details',
  templateUrl: './movie-details.component.html',
  styleUrls: ['./movie-details.component.css']
})
export class MovieDetailsComponent implements OnInit {
  movieDetails:Movies[]=[];
  popbackground:number=1;
  
  constructor(private dialog:MatDialog,
    private activatedRoute:ActivatedRoute,
    private sharedservice:SharedService
    ) {}
  
  ngOnInit(): void {
    //1.retriving the data from the URL and storing in movieDetails
     this.activatedRoute.params.subscribe((param:any)=>{this.movieDetails.push(param);});
     this.sharedservice.setAllDetails(this.movieDetails);

   }

  //2.opening the form
  bookListener(){
  
   this.dialog.open(DialogComponent,{
      width:'30%',
      backdropClass: "bdrop",
      id: 'dialogTrasparent',
      
    });
 }
  

  
 
}
