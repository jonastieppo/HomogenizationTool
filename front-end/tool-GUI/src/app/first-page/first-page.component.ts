import { Component } from '@angular/core';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { Observable } from 'rxjs';
import { map, shareReplay } from 'rxjs/operators';

@Component({
  selector: 'app-first-page',
  templateUrl: './first-page.component.html',
  styleUrls: ['./first-page.component.css']
})
export class FirstPageComponent {

  fiber_content: boolean = false;
  matrix_content: boolean = false;
  dashboardcontent: boolean = true;

  isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
    .pipe(
      map(result => result.matches),
      shareReplay()
    );

  toogleOnOffDashboardContent(dashboard_toogle:boolean):void{
    this.dashboardcontent=!dashboard_toogle
  }
  showfibers():void {
    this.fiber_content=!this.fiber_content
    this.matrix_content=false
    this.toogleOnOffDashboardContent(this.fiber_content)
    
  }
  showmatrix():void {
    this.matrix_content=!this.matrix_content
    this.fiber_content=false
    this.toogleOnOffDashboardContent(this.matrix_content)

    
  }

  constructor(private breakpointObserver: BreakpointObserver) {}

}
