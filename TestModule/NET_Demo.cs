using System;
using Vector.Tools;
using Vector.CANoe.Runtime;
using Vector.CANoe.Sockets;
using Vector.CANoe.Threading;
using Vector.Diagnostics;
using Vector.Scripting.UI;
using Vector.CANoe.TFS;
using Vector.CANoe.VTS;
using NetworkDB;

public class NET_Demo : TestModule
{
    public override void Main()
    {
// The title is written to the report
    Title = "C# Test Module";
    // Diagnostics test using the Vector Diagnostics Library
    TestGroupBegin("Engine Test ","");
      EngineSpeedTest();
    TestGroupEnd();
		
    }

 // Test cases need to be marked with an attribute:
 [TestCase("EngineSpeed Test")]
 public void EngineSpeedTest()
 {
	 Report.TestStep("Start engine:");
	 // Setting bus signal EngineSpeed to 1000:
	 EngineSpeed.Value = 1000;
	 // Waiting 100ms for the SigEngine signal being 1000:
	 Execution.Wait(100);
	 if (EngineSpeed.Value == 1000)
		Report.TestStepPass("Engine is running.");
	 else
		Report.TestStepFail("Engine is not running.");
 }
}