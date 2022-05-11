#
# PySNMP MIB module CALIX-SMI (http://snmplabs.com/pysmi)
# ASN.1 source file:///mnt/d/Data/MIBS/text_mibs/calix/CALIX-SMI
# Produced by pysmi-0.3.4 at Tue Jan 25 21:31:43 2022
# On host QS-IL-LT-COSTAY platform Linux version 5.10.60.1-microsoft-standard-WSL2 by user coye
# Using Python version 2.7.18 (default, Mar  8 2021, 13:02:45) 
#
Integer, ObjectIdentifier, OctetString = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
NamedValues, = mibBuilder.importSymbols("ASN1-ENUMERATION", "NamedValues")
ConstraintsUnion, SingleValueConstraint, ConstraintsIntersection, ValueSizeConstraint, ValueRangeConstraint = mibBuilder.importSymbols("ASN1-REFINEMENT", "ConstraintsUnion", "SingleValueConstraint", "ConstraintsIntersection", "ValueSizeConstraint", "ValueRangeConstraint")
NotificationGroup, ModuleCompliance = mibBuilder.importSymbols("SNMPv2-CONF", "NotificationGroup", "ModuleCompliance")
Integer32, MibScalar, MibTable, MibTableRow, MibTableColumn, NotificationType, MibIdentifier, IpAddress, TimeTicks, Counter64, Unsigned32, enterprises, iso, Gauge32, ModuleIdentity, ObjectIdentity, Bits, Counter32 = mibBuilder.importSymbols("SNMPv2-SMI", "Integer32", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "NotificationType", "MibIdentifier", "IpAddress", "TimeTicks", "Counter64", "Unsigned32", "enterprises", "iso", "Gauge32", "ModuleIdentity", "ObjectIdentity", "Bits", "Counter32")
DisplayString, TextualConvention = mibBuilder.importSymbols("SNMPv2-TC", "DisplayString", "TextualConvention")
calixNetworks = ModuleIdentity((1, 3, 6, 1, 4, 1, 6321))
calixNetworks.setRevisions(('2000-08-31 00:26',))
if mibBuilder.loadTexts: calixNetworks.setLastUpdated('200008310026Z')
if mibBuilder.loadTexts: calixNetworks.setOrganization('Calix Networks, Inc.')
calixRegistrations = ObjectIdentity((1, 3, 6, 1, 4, 1, 6321, 1))
if mibBuilder.loadTexts: calixRegistrations.setStatus('current')
calixModules = ObjectIdentity((1, 3, 6, 1, 4, 1, 6321, 1, 1))
if mibBuilder.loadTexts: calixModules.setStatus('current')
calixProducts = ObjectIdentity((1, 3, 6, 1, 4, 1, 6321, 1, 2))
if mibBuilder.loadTexts: calixProducts.setStatus('current')
calixManagement = ObjectIdentity((1, 3, 6, 1, 4, 1, 6321, 2))
if mibBuilder.loadTexts: calixManagement.setStatus('current')
mibBuilder.exportSymbols("CALIX-SMI", calixProducts=calixProducts, calixRegistrations=calixRegistrations, calixNetworks=calixNetworks, calixModules=calixModules, PYSNMP_MODULE_ID=calixNetworks, calixManagement=calixManagement)
