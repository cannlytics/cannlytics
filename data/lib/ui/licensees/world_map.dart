// // <https://gist.github.com/pskink/afd4f20a40ae7756555877ec030daa46>

// import 'dart:math';
// import 'dart:ui';

// import 'package:collection/collection.dart';
// import 'package:flutter/material.dart';
// import 'package:flutter/rendering.dart';
// import 'package:flutter/services.dart';
// import 'package:path_drawing/path_drawing.dart';
// import 'package:xml/xml.dart';

// class WorldMap extends StatefulWidget {
//   @override
//   State<WorldMap> createState() => _WorldMapState();
// }

// class _WorldMapState extends State<WorldMap> with TickerProviderStateMixin {
//   late final actrl = AnimationController(
//       vsync: this, duration: const Duration(milliseconds: 500));
//   WorldData? worldData;
//   TransformationController? tctrl;
//   late Animation<Matrix4> animation;
//   late ExtendedViewport extendedViewport;

//   @override
//   void initState() {
//     super.initState();
//     actrl.addListener(() => tctrl?.value = animation.value);
//     _parse().then((value) {
//       setState(() => worldData = value);
//     });
//   }

//   Matrix4 rectToRect(
//     Rect src,
//     Rect dst, {
//     BoxFit fit = BoxFit.contain,
//     Alignment alignment = Alignment.center,
//   }) {
//     FittedSizes fs = applyBoxFit(fit, src.size, dst.size);
//     double scaleX = fs.destination.width / fs.source.width;
//     double scaleY = fs.destination.height / fs.source.height;
//     Size fittedSrc = Size(src.width * scaleX, src.height * scaleY);
//     Rect out = alignment.inscribe(fittedSrc, dst);

//     return Matrix4.identity()
//       ..translate(out.left, out.top)
//       ..scale(scaleX, scaleY)
//       ..translate(-src.left, -src.top);
//   }

//   Matrix4 _zoomTo(String id, Size size) {
//     return rectToRect(worldData!.countries[id]!.rect, Offset.zero & size,
//         fit: BoxFit.contain);
//   }

//   TransformationController _initController(Size size) {
//     final matrix = rectToRect(Offset.zero & worldData!.size, Offset.zero & size,
//         fit: BoxFit.cover);
//     final ctrl = TransformationController(matrix);
//     extendedViewport = ExtendedViewport(
//       ctrl: ctrl,
//       cacheFactor: 1.75,
//     );

//     Future.delayed(const Duration(milliseconds: 1500), () {
//       // initial zoom to thailand
//       animation = Matrix4Tween(
//         begin: ctrl.value,
//         end: _zoomTo('TH', size),
//       ).animate(actrl);
//       actrl
//         ..value = 0
//         ..animateTo(1,
//             curve: Curves.easeInExpo,
//             duration: const Duration(milliseconds: 2500));
//     });
//     return ctrl;
//   }

//   @override
//   Widget build(BuildContext context) {
//     if (worldData == null) {
//       return const Center(child: CircularProgressIndicator());
//     }
//     return Theme(
//       data: Theme.of(context).copyWith(
//         splashFactory: _InkFactory(),
//       ),
//       child: LayoutBuilder(builder: (context, constraints) {
//         tctrl ??= _initController(constraints.biggest);
//         extendedViewport.size = constraints.biggest;
//         return ColoredBox(
//           color: Colors.blue.shade200,
//           child: InteractiveViewer(
//             constrained: false,
//             transformationController: tctrl,
//             maxScale: 50,
//             child: Flow(
//               delegate: WorldMapDelegate(worldData!, extendedViewport),
//               children: worldData!.countries.values
//                   .map((country) =>
//                       _countryBuilder(country, constraints.biggest))
//                   .toList(),
//             ),
//           ),
//         );
//       }),
//     );
//   }

//   Widget _countryBuilder(Country country, Size size) {
//     final shape = CountryBorder(country.path.shift(-country.rect.topLeft));
//     return DecoratedBox(
//       decoration: ShapeDecoration(
//         shape: shape,
//         gradient: country.gradient,
//         shadows: const [
//           BoxShadow(blurRadius: 0.5),
//           BoxShadow(blurRadius: 0.5, offset: Offset(0.5, 0.5)),
//         ],
//       ),
//       child: Material(
//         type: MaterialType.transparency,
//         clipBehavior: Clip.antiAlias,
//         shape: shape,
//         child: InkWell(
//           highlightColor: Colors.transparent,
//           onTap: () {
//             print('${country.title} (${country.id}) clicked');
//             final begin = tctrl!.value;
//             final end = _zoomTo(country.id, size);
//             if (tctrl!.value != end) {
//               animation = Matrix4Tween(
//                 begin: begin,
//                 end: end,
//               ).chain(CurveTween(curve: Curves.easeInOut)).animate(actrl);
//               actrl.forward(from: 0);
//             }
//           },
//           child: Center(
//               child: Text(
//             country.id,
//             textScaleFactor: 0.1,
//           )),
//         ),
//       ),
//     );
//   }

//   @override
//   void dispose() {
//     super.dispose();
//     actrl.dispose();
//     tctrl?.dispose();
//   }

//   Future<WorldData> _parse() async {
//     // get it from https://mapsvg.com/static/maps/geo-calibrated/world.svg
//     // more maps: https://mapsvg.com/maps
//     final xml = await rootBundle.loadString('world.svg');

//     final doc = XmlDocument.parse(xml);
//     final w = double.parse(doc.rootElement.getAttribute('width')!);
//     final h = double.parse(doc.rootElement.getAttribute('height')!);

//     List<Color> colors(double h) {
//       return [
//         HSVColor.fromAHSV(1, h * 360, 1, 0.9).toColor(),
//         HSVColor.fromAHSV(1, h * 360, 1, 0.3).toColor(),
//       ];
//     }

//     const padding = EdgeInsets.all(40);
//     final allCountries = doc.rootElement.findElements('path');
//     final numCountries = allCountries.length;
//     final countries = allCountries.mapIndexed((i, country) => Country(
//           path: parseSvgPathData(country.getAttribute('d')!)
//               .shift(padding.topLeft),
//           id: country.getAttribute('id') ?? 'id_$i ???',
//           title: country.getAttribute('title') ?? 'title_$i ???',
//           gradient: LinearGradient(
//             colors: colors(i / numCountries),
//             stops: const [0.2, 1],
//           ),
//           seqNo: i,
//         ));
//     return WorldData(
//       size: Size(w + padding.horizontal, h + padding.vertical),
//       countries: {
//         for (final country in countries) country.id: country,
//       },
//     );
//   }
// }

// class WorldMapDelegate extends FlowDelegate {
//   WorldMapDelegate(this.worldData, this.extendedViewport)
//       : super(repaint: extendedViewport);

//   final WorldData worldData;
//   final ValueNotifier<Rect> extendedViewport;

//   @override
//   void paintChildren(FlowPaintingContext context) {
//     final filteredCountries = worldData.countries.values
//         .where((country) => country.rect.overlaps(extendedViewport.value));
//     for (final country in filteredCountries) {
//       final offset = country.rect.topLeft;
//       context.paintChild(country.seqNo,
//           transform: Matrix4.translationValues(offset.dx, offset.dy, 0));
//     }
//     print('paintChildren, ${filteredCountries.map((c) => c.id)}');
//   }

//   @override
//   BoxConstraints getConstraintsForChild(int i, BoxConstraints constraints) {
//     // print('getConstraintsForChild $i');
//     final country = worldData.countries.values.elementAt(i);
//     return BoxConstraints.tight(country.rect.size);
//   }

//   @override
//   Size getSize(BoxConstraints constraints) => worldData.size;

//   @override
//   bool shouldRepaint(covariant FlowDelegate oldDelegate) => false;
// }

// class WorldData {
//   WorldData({
//     required this.size,
//     required this.countries,
//   });

//   final Size size;
//   final Map<String, Country> countries;
// }

// class Country {
//   Country({
//     required this.path,
//     required this.id,
//     required this.title,
//     required this.gradient,
//     required this.seqNo,
//   }) : rect = path.getBounds();

//   final Path path;
//   final Rect rect;
//   final String id;
//   final String title;
//   final Gradient gradient;
//   final int seqNo;
// }

// class ExtendedViewport extends ValueNotifier<Rect> {
//   ExtendedViewport({
//     required this.ctrl,
//     required this.cacheFactor,
//   }) : super(Rect.largest) {
//     ctrl.addListener(_buildViewport);
//   }

//   final TransformationController ctrl;
//   final double cacheFactor;
//   Size _size = Size.zero;
//   set size(Size size) {
//     if (size != _size) {
//       print('setting ExtendedViewport size: $size');
//       _size = size;
//     }
//   }

//   Rect innerRect = Rect.zero;
//   double prevScale = 0;

//   _buildViewport() {
//     assert(_size != Size.zero);
//     final offset = ctrl.toScene(_size.center(Offset.zero));
//     final scale = ctrl.value.getMaxScaleOnAxis();

//     if (!innerRect.contains(offset) || scale != prevScale) {
//       prevScale = scale;
//       value = Rect.fromCenter(
//         center: offset,
//         width: _size.width * cacheFactor / scale,
//         height: _size.height * cacheFactor / scale,
//       );
//       // print('value: $value');
//       innerRect = EdgeInsets.symmetric(
//         horizontal: _size.width * 0.5 / scale,
//         vertical: _size.height * 0.5 / scale,
//       ).deflateRect(value);
//     }
//   }
// }

// class CountryBorder extends ShapeBorder {
//   const CountryBorder(this.path);

//   final Path path;

//   @override
//   EdgeInsetsGeometry get dimensions => EdgeInsets.zero;

//   @override
//   Path getInnerPath(Rect rect, {TextDirection? textDirection}) =>
//       getOuterPath(rect);

//   @override
//   Path getOuterPath(Rect rect, {TextDirection? textDirection}) {
//     return rect.topLeft == Offset.zero ? path : path.shift(rect.topLeft);
//   }

//   @override
//   void paint(Canvas canvas, Rect rect, {TextDirection? textDirection}) {
//     canvas
//       ..save()
//       ..clipPath(path)
//       ..drawPath(
//           path,
//           Paint()
//             ..style = PaintingStyle.stroke
//             ..strokeWidth = 0.25
//             ..color = Colors.white38)
//       ..restore();
//   }

//   @override
//   ShapeBorder scale(double t) => this;
// }

// const Duration _kDuration = Duration(milliseconds: 650);

// class _InkFactory extends InteractiveInkFeatureFactory {
//   @override
//   InteractiveInkFeature create(
//       {required MaterialInkController controller,
//       required RenderBox referenceBox,
//       required Offset position,
//       required Color color,
//       required TextDirection textDirection,
//       bool containedInkWell = false,
//       RectCallback? rectCallback,
//       BorderRadius? borderRadius,
//       ShapeBorder? customBorder,
//       double? radius,
//       VoidCallback? onRemoved}) {
//     return _InkFeature(
//         controller: controller,
//         referenceBox: referenceBox,
//         color: color,
//         position: position);
//   }
// }

// class _InkFeature extends InteractiveInkFeature {
//   _InkFeature(
//       {required MaterialInkController controller,
//       required RenderBox referenceBox,
//       required Color color,
//       required this.position})
//       : super(
//             controller: controller, referenceBox: referenceBox, color: color) {
//     _controller =
//         AnimationController(duration: _kDuration, vsync: controller.vsync)
//           ..addListener(controller.markNeedsPaint)
//           ..forward();
//     controller.addInkFeature(this);
//   }

//   static const gradient = LinearGradient(
//     colors: [Colors.amber, Colors.deepOrange],
//   );

//   late AnimationController _controller;
//   final Offset position;

//   @override
//   void confirm() => _controller.reverse().then((value) => dispose());

//   @override
//   void cancel() => _controller.reverse().then((value) => dispose());

//   @override
//   void dispose() {
//     // print('dispose');
//     super.dispose();
//     _controller.dispose();
//   }

//   @override
//   void paintFeature(Canvas canvas, Matrix4 transform) {
//     final scale = referenceBox.getTransformTo(null).getMaxScaleOnAxis();
//     final t = Curves.easeInOut.transform(_controller.value);
//     final rect = Offset.zero & referenceBox.size;
//     final side = 2 * rect.bottomRight.distance;

//     final paint = Paint()
//       ..color = Color.fromARGB(
//           lerpDouble(100, 255, _controller.value)!.toInt(), 0, 0, 0)
//       ..shader = gradient.createShader(rect);
//     final matrix = composeMatrixFromOffsets(
//       anchor: position,
//       translate: position,
//       rotation: pi * .75 * t,
//     );
//     final hFactor = const Cubic(1, 0, 1, 1).transform(t);
//     final path = Path()
//       ..addOval(
//         Rect.fromCenter(
//             center: position,
//             width: side * _controller.value,
//             height: (48 / scale + side * hFactor) * _controller.value),
//       );
//     canvas
//       ..save()
//       ..transform(matrix.storage)
//       ..drawPath(path, paint)
//       ..restore();
//   }
// }

// Matrix4 composeMatrixFromOffsets({
//   double scale = 1,
//   double rotation = 0,
//   Offset translate = Offset.zero,
//   Offset anchor = Offset.zero,
// }) {
//   final double c = cos(rotation) * scale;
//   final double s = sin(rotation) * scale;
//   final double dx = translate.dx - c * anchor.dx + s * anchor.dy;
//   final double dy = translate.dy - s * anchor.dx - c * anchor.dy;
//   return Matrix4(c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, dx, dy, 0, 1);
// }
