import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { SharedService } from '../Services/shared.service';
import { UserService } from '../Services/user.service';
import { Movies } from '../Utilities/Movie';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ApiConsumingService } from '../Services/api-consuming.service';
import { MovieDetailsComponent } from '../movie-details/movie-details.component';


@Component({
  selector: 'app-dialog',
  templateUrl: './dialog.component.html',
  styleUrls: ['./dialog.component.css']
})
export class DialogComponent implements OnInit {
  inputForm:FormGroup;
  numberRegEx = "^[1-9][0-9]*$";
  movieDetails:any;
  user:any;
  remaining_tickets:number=0;
  index:number=-1;
  localstoragedata:any;
  fillOrUpdate:number=0;
  actionbtn:string="Save";

  constructor(private activatedRoute:ActivatedRoute,@Inject (MAT_DIALOG_DATA) public editData:any,
    private userService:UserService,private sharedservice:SharedService,private apiservice :ApiConsumingService,
    public dialogRef: MatDialogRef<MovieDetailsComponent>,
    private sharedService:SharedService) {
    this.inputForm=new FormGroup({
      name:new FormControl('',[Validators.required,Validators.minLength(4)]),
      email:new FormControl('',[Validators.required,Validators.email]),
      showtime:new FormControl('',Validators.required),
      noOfTickets:new FormControl('',[Validators.required,Validators.pattern(this.numberRegEx)]),
    });
   }

  ngOnInit(): void {
    this.movieDetails=this.sharedservice.getMovieDetails();
    if(this.editData){
      this.actionbtn="Update";
      this.inputForm.controls['name'].setValue(this.editData.name);
      this.inputForm.controls['email'].setValue(this.editData.email);
      this.inputForm.controls['showtime'].setValue(this.editData.showtime);
      this.inputForm.controls['noOfTickets'].setValue(this.editData.noOfTickets);
    }
    
    this.getIndex();
  }

   get f(){
    return this.inputForm.controls;
    }
 
   getIndex(){
    this.localstoragedata = JSON.parse(localStorage.getItem('Users') || '{}');
    const isFound = this.localstoragedata.some((element: any) => {
      if (this.editData.email === element.email) {
        this.index = this.localstoragedata.indexOf(element);
   }
  });
}

 //Submitting the form and 
  onSubmitHandler(myform: any) {
  if(this.inputForm.valid){
  this.user=this.inputForm.value;
 
   if(this.editData){
    this.remaining_tickets = this.editData.remainingTickets;
    if (this.editData.noOfTickets != this.user.noOfTickets) {
      this.remaining_tickets += this.editData.noOfTickets - this.user.noOfTickets;
      this.user['remainingTickets'] = this.remaining_tickets;
    }
    else {
      this.user['remainingTickets'] = this.remaining_tickets;
    }
    console.log("remaining Tickets =",this.user.remainingTickets);
    console.log("this.user",this.user);
    var variable = JSON.parse(localStorage.getItem('Users') || '{}');
    variable[this.index].name = this.user.name;
    variable[this.index].email = this.user.email;
    variable[this.index].noOfTickets = this.user.noOfTickets;
    variable[this.index].time = this.user.time;
    variable[this.index].remainingTickets = this.user.remainingTickets;
    localStorage.setItem('Users', JSON.stringify(variable));
    this.updateUrl();
    this.sharedService.sharedNotification("Details Updated Successfully","ok");

   }
   else{
   console.log("data is saving.....");
   this.user['id']=this.movieDetails[0].id;
   this.user['movieName']=this.movieDetails[0].name;
   this.user['duration']=this.movieDetails[0].Duration;
   this.user['price']=this.movieDetails[0].Price;
   this.remaining_tickets=(this.movieDetails[0].Tickets)-(this.user.noOfTickets);
   this.user['remainingTickets']=this.remaining_tickets;
   const data={
    id:this.movieDetails[0].id,
    description :this.movieDetails[0].description,
    name :this. movieDetails[0].name,
    Price :this.movieDetails[0].Price,
    Tickets :this.remaining_tickets, 
    Duration :this.movieDetails[0].Duration,
    Image :this.movieDetails[0].Image,
    Desc2:this.movieDetails[0].Desc2,
  }

   this.userService.updateTickets(data,this.movieDetails[0].id).subscribe((data:Movies)=>{console.log("after updating",data);
  });
  
   this.userService.addUser(this.user);
   this.sharedService.sharedNotification("Tickets Saved Successfully","ok");
  
}
this.dialogRef.close();
  }
}

movies:any;
updateUrl(){

  var id=this.editData.id;

  this.apiservice.getMovieDetailsById(id).subscribe((data:any) => {
  this.movies = data;
  console.log(this.movies)
  const databody={
    id:this.editData.id,
    description :this.movies.description,
    name :this.editData.movieName,
    Price :this.editData.price,
    Tickets :this.user.remainingTickets, 
    Duration :this.editData.duration,
    Image :this.movies.Image,
    Desc2:this.movies.Desc2,

   }
   console.log(databody);
   this.userService.updateTicketsByUpdatedUser(databody,this.editData.id).subscribe((data:Movies)=>{console.log("after updating",data);});
   
});
}

}
